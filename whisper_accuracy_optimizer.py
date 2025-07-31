#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper 識別準確度優化器
專門解決 Whisper 模型識別不正確的問題
"""

import os
import re
import json
import warnings
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import difflib

# 抑制 Whisper 警告
warnings.filterwarnings("ignore", message=".*Failed to launch Triton kernels.*")
warnings.filterwarnings("ignore", message=".*falling back to a slower.*")

class WhisperAccuracyOptimizer:
    """Whisper 識別準確度優化器"""
    
    def __init__(self):
        self.load_optimization_config()
        self.setup_language_specific_rules()
        
    def load_optimization_config(self):
        """載入優化配置"""
        self.optimization_config = {
            # 基礎參數優化
            "base_params": {
                "temperature": [0.0, 0.2, 0.5],  # 多溫度嘗試
                "no_speech_threshold": 0.6,
                "compression_ratio_threshold": 2.4,
                "logprob_threshold": -1.0,
                "condition_on_previous_text": False,
                "initial_prompt": None,
                "word_timestamps": True,
                "prepend_punctuations": "\"'([{-",
                "append_punctuations": "\"'.。,，!！?？:：\")]}、",
            },
            
            # 音樂模式優化
            "music_mode": {
                "temperature": [0.0, 0.3, 0.7],
                "no_speech_threshold": 0.3,
                "compression_ratio_threshold": 3.0,
                "logprob_threshold": -1.5,
                "best_of": 5,
                "beam_size": 5,
                "patience": 2.0,
                "length_penalty": 1.0,
                "suppress_tokens": [-1],  # 不抑制任何 token
                "without_timestamps": False,
            },
            
            # 語音模式優化
            "speech_mode": {
                "temperature": [0.0, 0.1],
                "no_speech_threshold": 0.6,
                "compression_ratio_threshold": 2.4,
                "logprob_threshold": -1.0,
                "best_of": 3,
                "beam_size": 3,
                "patience": 1.0,
                "length_penalty": 1.0,
            },
            
            # 高精度模式
            "high_accuracy_mode": {
                "temperature": [0.0],  # 最低溫度
                "no_speech_threshold": 0.8,
                "compression_ratio_threshold": 2.0,
                "logprob_threshold": -0.5,
                "best_of": 5,
                "beam_size": 5,
                "patience": 2.0,
                "length_penalty": 1.2,
            }
        }
    
    def setup_language_specific_rules(self):
        """設定語言特定的規則"""
        self.language_rules = {
            "ja": {
                "common_errors": {
                    # 常見的日文識別錯誤修正
                    "あの": ["あのー", "あのう", "あの〜"],
                    "そう": ["そうー", "そうう", "そう〜"],
                    "です": ["でーす", "ですー"],
                    "ます": ["まーす", "ますー"],
                    "ください": ["くださーい", "ください〜"],
                    "ありがとう": ["ありがとー", "ありがとうー"],
                    "こんにちは": ["こんにちわ", "こんにちはー"],
                    "すみません": ["すいません", "すみませーん"],
                },
                "filter_patterns": [
                    r"^[あーうーえーおー]+$",  # 只有長音的內容
                    r"^[。、！？]+$",  # 只有標點符號
                    r"^[♪♫♬♩]+$",  # 只有音樂符號
                    r"^[・]+$",  # 只有中點
                ],
                "meaningless_phrases": [
                    "あー", "うー", "えー", "おー",
                    "んー", "うん", "ええ",
                    "♪", "♫", "♬", "♩",
                    "ラララ", "ナナナ", "ハハハ",
                    "作詞", "作曲", "編曲",
                    "初音ミク", "ボーカロイド",
                ]
            },
            
            "en": {
                "common_errors": {
                    "yeah": ["yea", "yah", "ye"],
                    "okay": ["ok", "k"],
                    "alright": ["aight", "alrite"],
                    "because": ["cuz", "cos", "cause"],
                    "going to": ["gonna", "goin to"],
                    "want to": ["wanna", "wan to"],
                },
                "filter_patterns": [
                    r"^[aeiou]+$",  # 只有母音
                    r"^[hmm]+$",  # hmm 類聲音
                    r"^[uh]+$",  # uh 類聲音
                ],
                "meaningless_phrases": [
                    "uh", "um", "er", "ah",
                    "hmm", "mhm", "mm",
                    "la la la", "na na na",
                    "music", "song", "lyrics",
                ]
            },
            
            "zh": {
                "common_errors": {
                    "這個": ["這", "個"],
                    "那個": ["那", "個"],
                    "什麼": ["甚麼", "什么"],
                    "沒有": ["沒", "有"],
                    "可以": ["可", "以"],
                },
                "filter_patterns": [
                    r"^[啊呃嗯哦]+$",  # 語氣詞
                    r"^[。，！？]+$",  # 標點符號
                ],
                "meaningless_phrases": [
                    "啊", "呃", "嗯", "哦",
                    "這個", "那個", "然後",
                    "就是", "然後就",
                ]
            }
        }
    
    def optimize_whisper_params(self, 
                               content_type: str = "auto",
                               language: str = "auto",
                               quality_level: str = "high") -> Dict[str, Any]:
        """
        根據內容類型和語言優化 Whisper 參數
        
        Args:
            content_type: 內容類型 ("music", "speech", "mixed", "auto")
            language: 語言 ("ja", "en", "zh", "auto")
            quality_level: 品質等級 ("fast", "balanced", "high", "ultra")
        
        Returns:
            優化後的參數字典
        """
        base_params = self.optimization_config["base_params"].copy()
        
        # 根據內容類型調整參數
        if content_type == "music":
            base_params.update(self.optimization_config["music_mode"])
        elif content_type == "speech":
            base_params.update(self.optimization_config["speech_mode"])
        elif quality_level == "ultra":
            base_params.update(self.optimization_config["high_accuracy_mode"])
        
        # 根據語言調整參數
        if language == "ja":
            # 日文特殊優化
            base_params["initial_prompt"] = "以下は日本語の音声です。正確に転写してください。"
            base_params["suppress_tokens"] = []  # 不抑制日文特殊字符
        elif language == "en":
            base_params["initial_prompt"] = "The following is English speech. Please transcribe accurately."
        elif language == "zh":
            base_params["initial_prompt"] = "以下是中文語音，請準確轉錄。"
        
        # 根據品質等級調整
        if quality_level == "fast":
            base_params["temperature"] = [0.0]
            base_params["best_of"] = 1
        elif quality_level == "balanced":
            base_params["temperature"] = [0.0, 0.2]
            base_params["best_of"] = 3
        elif quality_level == "high":
            base_params["temperature"] = [0.0, 0.2, 0.5]
            base_params["best_of"] = 5
        elif quality_level == "ultra":
            base_params["temperature"] = [0.0, 0.1, 0.3, 0.5, 0.7]
            base_params["best_of"] = 5
            base_params["beam_size"] = 5
        
        return base_params
    
    def multi_pass_transcription(self, 
                                model, 
                                audio_file: str, 
                                params: Dict[str, Any],
                                language: str = "auto") -> Dict[str, Any]:
        """
        多次通過轉錄，選擇最佳結果
        
        Args:
            model: Whisper 模型
            audio_file: 音訊檔案路徑
            params: 轉錄參數
            language: 語言代碼
        
        Returns:
            最佳轉錄結果
        """
        results = []
        temperatures = params.get("temperature", [0.0])
        
        print(f"🔄 開始多次通過轉錄 (溫度值: {temperatures})")
        
        for i, temp in enumerate(temperatures):
            try:
                print(f"   第 {i+1}/{len(temperatures)} 次 (溫度: {temp})")
                
                current_params = params.copy()
                current_params["temperature"] = temp
                
                # 移除不是 Whisper API 參數的項目
                whisper_params = {k: v for k, v in current_params.items() 
                                if k not in ["temperature"]}  # temperature 會單獨處理
                
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    result = model.transcribe(
                        audio_file, 
                        temperature=temp,
                        **whisper_params
                    )
                
                # 計算結果品質分數
                quality_score = self.calculate_quality_score(result, language)
                results.append({
                    "result": result,
                    "temperature": temp,
                    "quality_score": quality_score
                })
                
                print(f"   品質分數: {quality_score:.3f}")
                
            except Exception as e:
                print(f"   ⚠️ 溫度 {temp} 轉錄失敗: {e}")
                continue
        
        if not results:
            raise Exception("所有溫度設定都轉錄失敗")
        
        # 選擇品質分數最高的結果
        best_result = max(results, key=lambda x: x["quality_score"])
        print(f"✅ 選擇最佳結果 (溫度: {best_result['temperature']}, 分數: {best_result['quality_score']:.3f})")
        
        return best_result["result"]
    
    def calculate_quality_score(self, result: Dict[str, Any], language: str) -> float:
        """
        計算轉錄結果的品質分數
        
        Args:
            result: Whisper 轉錄結果
            language: 語言代碼
        
        Returns:
            品質分數 (0-1)
        """
        if not result.get("segments"):
            return 0.0
        
        total_score = 0.0
        total_segments = len(result["segments"])
        
        for segment in result["segments"]:
            segment_score = 0.0
            
            # 1. 基於平均對數機率的分數 (40%)
            if "avg_logprob" in segment:
                # 將對數機率轉換為 0-1 分數
                logprob_score = max(0, min(1, (segment["avg_logprob"] + 3) / 3))
                segment_score += logprob_score * 0.4
            
            # 2. 基於壓縮比的分數 (20%)
            if "compression_ratio" in segment:
                # 理想的壓縮比在 1.5-2.5 之間
                compression_ratio = segment["compression_ratio"]
                if 1.5 <= compression_ratio <= 2.5:
                    compression_score = 1.0
                elif compression_ratio < 1.5:
                    compression_score = compression_ratio / 1.5
                else:
                    compression_score = max(0, 1 - (compression_ratio - 2.5) / 2.5)
                segment_score += compression_score * 0.2
            
            # 3. 基於文字品質的分數 (30%)
            text = segment.get("text", "").strip()
            text_score = self.evaluate_text_quality(text, language)
            segment_score += text_score * 0.3
            
            # 4. 基於時間一致性的分數 (10%)
            duration = segment.get("end", 0) - segment.get("start", 0)
            if duration > 0 and len(text) > 0:
                # 理想的語速約為每秒 2-8 個字符
                chars_per_second = len(text) / duration
                if 2 <= chars_per_second <= 8:
                    timing_score = 1.0
                elif chars_per_second < 2:
                    timing_score = chars_per_second / 2
                else:
                    timing_score = max(0, 1 - (chars_per_second - 8) / 8)
                segment_score += timing_score * 0.1
            
            total_score += segment_score
        
        return total_score / total_segments if total_segments > 0 else 0.0
    
    def evaluate_text_quality(self, text: str, language: str) -> float:
        """
        評估文字品質
        
        Args:
            text: 要評估的文字
            language: 語言代碼
        
        Returns:
            文字品質分數 (0-1)
        """
        if not text or len(text.strip()) < 2:
            return 0.0
        
        score = 1.0
        
        # 檢查是否包含無意義的內容
        if language in self.language_rules:
            rules = self.language_rules[language]
            
            # 檢查過濾模式
            for pattern in rules.get("filter_patterns", []):
                if re.match(pattern, text.strip()):
                    score *= 0.1
                    break
            
            # 檢查無意義短語
            for phrase in rules.get("meaningless_phrases", []):
                if phrase in text.lower():
                    score *= 0.5
        
        # 檢查重複字符
        if len(set(text.replace(" ", ""))) < len(text.replace(" ", "")) * 0.3:
            score *= 0.6  # 字符重複度太高
        
        # 檢查長度合理性
        if len(text) < 3:
            score *= 0.7
        elif len(text) > 200:
            score *= 0.9  # 太長的句子可能有問題
        
        return score
    
    def post_process_segments(self, 
                             segments: List[Dict[str, Any]], 
                             language: str = "auto",
                             filter_repetitive: bool = True,
                             merge_short_segments: bool = True) -> List[Dict[str, Any]]:
        """
        後處理轉錄片段
        
        Args:
            segments: 原始片段列表
            language: 語言代碼
            filter_repetitive: 是否過濾重複內容
            merge_short_segments: 是否合併短片段
        
        Returns:
            處理後的片段列表
        """
        if not segments:
            return []
        
        print(f"🔧 開始後處理 {len(segments)} 個片段")
        
        # 1. 基本清理
        cleaned_segments = []
        for segment in segments:
            text = segment.get("text", "").strip()
            
            # 跳過空白內容
            if not text or len(text) < 2:
                continue
            
            # 語言特定的清理
            if language in self.language_rules:
                text = self.clean_text_by_language(text, language)
                if not text:
                    continue
            
            segment["text"] = text
            cleaned_segments.append(segment)
        
        print(f"   清理後剩餘: {len(cleaned_segments)} 個片段")
        
        # 2. 過濾重複內容
        if filter_repetitive:
            cleaned_segments = self.filter_repetitive_segments(cleaned_segments)
            print(f"   過濾重複後剩餘: {len(cleaned_segments)} 個片段")
        
        # 3. 合併短片段
        if merge_short_segments:
            cleaned_segments = self.merge_short_segments(cleaned_segments)
            print(f"   合併短片段後剩餘: {len(cleaned_segments)} 個片段")
        
        # 4. 最終品質檢查
        final_segments = []
        for segment in cleaned_segments:
            text_quality = self.evaluate_text_quality(segment["text"], language)
            if text_quality > 0.3:  # 只保留品質分數 > 0.3 的片段
                final_segments.append(segment)
        
        print(f"✅ 最終保留: {len(final_segments)} 個高品質片段")
        return final_segments
    
    def clean_text_by_language(self, text: str, language: str) -> str:
        """
        根據語言清理文字
        
        Args:
            text: 原始文字
            language: 語言代碼
        
        Returns:
            清理後的文字
        """
        if language not in self.language_rules:
            return text
        
        rules = self.language_rules[language]
        
        # 檢查過濾模式
        for pattern in rules.get("filter_patterns", []):
            if re.match(pattern, text.strip()):
                return ""  # 完全過濾掉
        
        # 修正常見錯誤
        for correct, errors in rules.get("common_errors", {}).items():
            for error in errors:
                text = text.replace(error, correct)
        
        # 移除無意義短語（如果整個文字就是無意義短語）
        meaningless = rules.get("meaningless_phrases", [])
        if text.strip().lower() in [phrase.lower() for phrase in meaningless]:
            return ""
        
        return text.strip()
    
    def filter_repetitive_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """過濾重複的片段"""
        if len(segments) <= 1:
            return segments
        
        filtered = [segments[0]]  # 保留第一個片段
        
        for current in segments[1:]:
            current_text = current["text"].strip().lower()
            
            # 檢查與前面幾個片段的相似度
            is_repetitive = False
            for prev in filtered[-3:]:  # 檢查最近3個片段
                prev_text = prev["text"].strip().lower()
                
                # 完全相同
                if current_text == prev_text:
                    is_repetitive = True
                    break
                
                # 高度相似
                similarity = difflib.SequenceMatcher(None, current_text, prev_text).ratio()
                if similarity > 0.8:
                    is_repetitive = True
                    break
                
                # 包含關係
                if len(current_text) > 10 and len(prev_text) > 10:
                    if current_text in prev_text or prev_text in current_text:
                        is_repetitive = True
                        break
            
            if not is_repetitive:
                filtered.append(current)
        
        return filtered
    
    def merge_short_segments(self, segments: List[Dict[str, Any]], 
                           min_duration: float = 1.0,
                           max_gap: float = 2.0) -> List[Dict[str, Any]]:
        """
        合併過短的片段
        
        Args:
            segments: 片段列表
            min_duration: 最小持續時間（秒）
            max_gap: 最大間隔時間（秒）
        
        Returns:
            合併後的片段列表
        """
        if len(segments) <= 1:
            return segments
        
        merged = []
        current_segment = segments[0].copy()
        
        for next_segment in segments[1:]:
            current_duration = current_segment["end"] - current_segment["start"]
            gap = next_segment["start"] - current_segment["end"]
            
            # 如果當前片段太短且與下一個片段間隔不大，則合併
            if current_duration < min_duration and gap <= max_gap:
                # 合併文字和時間
                current_segment["text"] += " " + next_segment["text"]
                current_segment["end"] = next_segment["end"]
                
                # 合併其他屬性（如果存在）
                if "avg_logprob" in current_segment and "avg_logprob" in next_segment:
                    # 加權平均
                    w1 = current_duration
                    w2 = next_segment["end"] - next_segment["start"]
                    total_weight = w1 + w2
                    if total_weight > 0:
                        current_segment["avg_logprob"] = (
                            current_segment["avg_logprob"] * w1 + 
                            next_segment["avg_logprob"] * w2
                        ) / total_weight
            else:
                # 不合併，保存當前片段並開始新的片段
                merged.append(current_segment)
                current_segment = next_segment.copy()
        
        # 添加最後一個片段
        merged.append(current_segment)
        
        return merged
    
    def generate_optimized_srt(self, 
                              result: Dict[str, Any], 
                              language: str = "auto",
                              filter_repetitive: bool = True,
                              merge_short_segments: bool = True) -> str:
        """
        生成優化的 SRT 字幕
        
        Args:
            result: Whisper 轉錄結果
            language: 語言代碼
            filter_repetitive: 是否過濾重複內容
            merge_short_segments: 是否合併短片段
        
        Returns:
            SRT 格式字幕內容
        """
        if not result.get("segments"):
            return ""
        
        # 後處理片段
        processed_segments = self.post_process_segments(
            result["segments"],
            language=language,
            filter_repetitive=filter_repetitive,
            merge_short_segments=merge_short_segments
        )
        
        # 生成 SRT 內容
        srt_content = ""
        for i, segment in enumerate(processed_segments, 1):
            start_time = self.seconds_to_srt_time(segment["start"])
            end_time = self.seconds_to_srt_time(segment["end"])
            text = segment["text"].strip()
            
            srt_content += f"{i}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{text}\n\n"
        
        return srt_content
    
    def seconds_to_srt_time(self, seconds: float) -> str:
        """將秒數轉換為 SRT 時間格式"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def save_optimization_report(self, 
                                original_segments: int,
                                final_segments: int,
                                quality_scores: List[float],
                                output_path: str):
        """保存優化報告"""
        report = {
            "optimization_summary": {
                "original_segments": original_segments,
                "final_segments": final_segments,
                "reduction_rate": (original_segments - final_segments) / original_segments if original_segments > 0 else 0,
                "average_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                "min_quality_score": min(quality_scores) if quality_scores else 0,
                "max_quality_score": max(quality_scores) if quality_scores else 0,
            },
            "recommendations": self.generate_recommendations(original_segments, final_segments, quality_scores)
        }
        
        report_path = output_path.replace(".srt", "_optimization_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 優化報告已保存至: {report_path}")
    
    def generate_recommendations(self, 
                               original_segments: int,
                               final_segments: int,
                               quality_scores: List[float]) -> List[str]:
        """生成優化建議"""
        recommendations = []
        
        if not quality_scores:
            return ["無法生成建議：缺少品質分數資料"]
        
        avg_quality = sum(quality_scores) / len(quality_scores)
        reduction_rate = (original_segments - final_segments) / original_segments if original_segments > 0 else 0
        
        if avg_quality < 0.5:
            recommendations.append("建議使用更大的模型（如 large）以提高識別準確度")
            recommendations.append("考慮使用高品質的音訊檔案作為輸入")
            recommendations.append("檢查音訊品質，確保沒有過多背景噪音")
        
        if reduction_rate > 0.5:
            recommendations.append("過濾了大量片段，可能需要調整過濾參數")
            recommendations.append("考慮降低品質閾值以保留更多內容")
        
        if reduction_rate < 0.1:
            recommendations.append("過濾效果有限，可能需要加強後處理")
            recommendations.append("考慮啟用更嚴格的重複內容過濾")
        
        if avg_quality > 0.8:
            recommendations.append("識別品質良好，當前設定適合此類內容")
        
        return recommendations if recommendations else ["當前優化效果良好，無需特別調整"]


# 使用範例
if __name__ == "__main__":
    optimizer = WhisperAccuracyOptimizer()
    
    # 示例：優化音樂內容的參數
    music_params = optimizer.optimize_whisper_params(
        content_type="music",
        language="ja",
        quality_level="ultra"
    )
    
    print("🎵 音樂模式優化參數:")
    for key, value in music_params.items():
        print(f"   {key}: {value}")