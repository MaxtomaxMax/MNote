import os
import json
from datetime import datetime
from pydub import AudioSegment
from opencc import OpenCC # 繁体转简体
cc = OpenCC('t2s')

from dotenv import load_dotenv
load_dotenv()
OPENAI_API = os.getenv("OPENAI_API")

os.environ["PATH"] += os.pathsep + "d:\\Software\\ffmpeg\\ffmpeg-7.1.1-essentials_build\\bin"  # 替换为实际路径
os.environ["PATH"] += os.pathsep + "d:\\nodejs"

AudioSegment.ffmpeg = "d:\\Software\\ffmpeg\\ffmpeg-7.1.1-essentials_build\\bin\\ffmpeg.exe"    # 显式指定可执行文件
AudioSegment.ffprobe = "d:\\Software\\ffmpeg\\ffmpeg-7.1.1-essentials_build\\bin\\ffprobe.exe"

import torch
import torchaudio
import whisper
from openai import OpenAI
from speechbrain.inference import SpeakerRecognition
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("audio2md_server")

class Audio2MDWhisper:
    def __init__(self, openai_key: str, openai_base_url: str = "https://api.openai.com/v1"):
        self.openai_key = openai_key
        self.openai_base_url = openai_base_url

        # 初始化模型
        self.whisper_model = whisper.load_model("base")  # 可换成 medium / large
        self.spk_model = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="audio_model"
        )

    def convert_to_wav(self, input_audio_path: str, output_audio_path: str = "converted.wav"):
        audio = AudioSegment.from_file(input_audio_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(output_audio_path, format="wav")
        return output_audio_path

    def split_audio_chunks(self, wav_path, chunk_duration_ms=5000):
        audio = AudioSegment.from_wav(wav_path)
        chunks = [audio[i:i+chunk_duration_ms] for i in range(0, len(audio), chunk_duration_ms)]
        chunk_paths = []
        for idx, chunk in enumerate(chunks):
            path = f"chunk_{idx}.wav"
            chunk.export(path, format="wav")
            chunk_paths.append(path)
        return chunk_paths

    def get_embedding(self, audio_path):
        signal, fs = torchaudio.load(audio_path)
        embeddings = self.spk_model.encode_batch(signal)
        return embeddings.squeeze(0)

    def cluster_speakers(self, embeddings, threshold=0.75):
        speakers = []
        anchors = []
        for emb in embeddings:
            if not anchors:
                anchors.append(emb)
                speakers.append(0)
            else:
                sims = [torch.nn.functional.cosine_similarity(emb, a).item() for a in anchors]
                if max(sims) > threshold:
                    speakers.append(sims.index(max(sims)))
                else:
                    anchors.append(emb)
                    speakers.append(len(anchors) - 1)
        return speakers

    def transcribe_chunks_whisper(self, chunk_paths, language='zh'):
        transcriptions = []
        for path in chunk_paths:
            result = self.whisper_model.transcribe(path, language=language)
            text = result.get("text", "").strip()
            transcriptions.append(text)
            with open(".\\audio2text\\trans2.json", "w") as f:
                json.dump(transcriptions, f)
            print("done")
        return transcriptions

    def summarize_text_with_gpt(self, text: str) -> str:
        client = OpenAI(api_key=self.openai_key, base_url=self.openai_base_url)
        
        prompt = f"""
请将以下音频转录文本整理为结构清晰的笔记。要求如下：

1. 用简洁、书面化语言表达，删除无意义的口语、重复、停顿等内容
2. 提炼并按逻辑结构分段，可使用标题、小标题来组织内容
3. 如有概念、要点或行动项，请用项目符号或编号清晰列出
4. 尽量保留原始语义，不要编造内容，但可以适度润色不通顺的地方
5. 如果能确定主题，请在文首添加一个简要标题

输出为 Markdown 格式：\n\n{text}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content

    def save_markdown(self, md_text: str, output_dir: str) -> str:
        os.makedirs(output_dir, exist_ok=True)
        filename = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_text)
        return file_path

    def process(self, audio_file: str, language: str, output_dir: str) -> str:
        wav_path = self.convert_to_wav(audio_file)
        chunk_paths = self.split_audio_chunks(wav_path)
        embeddings = [self.get_embedding(p) for p in chunk_paths]
        speakers = self.cluster_speakers(embeddings)
        transcriptions = self.transcribe_chunks_whisper(chunk_paths, language)
        raw_text = "".join(transcriptions)
        summary = self.summarize_text_with_gpt(raw_text)
        final_md = f"{summary}\n\n---\n# 原始文本 \n\n{cc.convert(raw_text)}"
        return self.save_markdown(final_md, output_dir)

@mcp.tool()
async def audio2md(audio_path, language="zh", output_dir="./outputs"):
    """
    将音频文件转换为结构化的Markdown笔记，包含内容摘要和详细转录文本。
    
    处理流程：
    1. 将输入音频转换为标准WAV格式
    2. 分割音频为5秒的片段
    3. 使用Whisper模型进行语音识别
    4. 使用ECAPA-TDNN模型进行说话人分离
    5. 通过GPT-4o整理为结构化笔记
    6. 生成包含摘要和详细记录的Markdown文件
    
    参数:
        audio_path (str): 输入音频文件路径，支持常见音频格式(mp3, wav, m4a等)
        language (str, optional): 音频语言代码，默认为"zh"(中文)。支持"en"等Whisper支持的语言
        output_dir (str, optional): 输出Markdown文件保存目录，默认为"./outputs"
    
    返回:
        str: 生成的Markdown文件绝对路径
    """
    converter = Audio2MDWhisper(openai_key=OPENAI_API, openai_base_url="https://vip.apiyi.com/v1")
    
    result = converter.process(audio_path, language, output_dir)
    return result

if __name__ == "__main__":
    mcp.run(transport='stdio')