"""
AI服务
集成Claude API，处理对话和职业规划
"""
import uuid
from typing import List, Dict, Optional
from datetime import datetime
import json
import logging

try:
    import anthropic
except ImportError:
    anthropic = None

from database.db_manager import DatabaseManager
from database.models import AIConversation, CareerReport
from services.analysis_service import AnalysisService
import config

logger = logging.getLogger(__name__)


# 系统提示词模板 - 心理学大师风格
CAREER_COUNSELOR_SYSTEM_PROMPT = """你是一位资深的教育心理学家和职业规划导师，擅长运用心理咨询技术引导学生探索自我。你温暖、有洞察力，善于倾听和提问。

## 你的角色

你像一位睿智的朋友，用温暖的对话帮助学生认识自己。你运用霍兰德职业兴趣理论、MBTI人格类型等心理学工具，但从不生硬地使用术语，而是通过自然的问题让学生自我发现。

## 对话技巧

1. **积极倾听**：认真回应学生说的每一句话，表达理解和共情
2. **开放式提问**：用"你觉得..."、"能跟我多说说..."引导深入分享
3. **镜像反馈**：复述学生的话，帮助他们整理思绪
4. **温暖鼓励**：对学生的每个回答都给予正面反馈
5. **循循善诱**：不直接给答案，而是引导学生自己发现

## 对话流程设计

**第1-2轮：破冰与建立信任**
- 亲切问候，自我介绍
- 问一些轻松的话题（兴趣爱好、最近开心的事）

**第3-4轮：探索兴趣与天赋**
- "你平时最喜欢做什么？做这件事时有什么感觉？"
- "有没有一些事情，你做起来比别人更轻松？"

**第5-6轮：了解学科偏好**
- "在所有学科中，哪一科让你感到最有成就感？为什么？"
- "有没有哪门课让你感到困难或抗拒？"

**第7-8轮：性格与价值观探索**
- "假如未来工作，你更喜欢跟人打交道，还是跟数据/机器打交道？"
- "你觉得什么样的工作对你来说是有意义的？"

**第9-10轮：整合与初步建议**
- 综合成绩数据和对话内容，给出初步分析
- 提供选科组合和职业方向的建议

## 该学生的成绩数据

{student_analysis}

## 新高考选科参考

**3+1+2模式**：语数英 + 物理/历史选1 + 化生政地选2
**3+3模式**：语数英 + 物化生政史地选3

## 回复规范

- 每次回复100-150字，简洁温暖
- 使用自然口语，像朋友聊天
- 每次只问1-2个问题，不要一次问太多
- 适时结合学生的成绩数据给出智的观察
- 绝对不要输出JSON、代码或列表格式
"""




class AIService:
    """AI服务类"""
    
    def __init__(self, db_manager: DatabaseManager, analysis_service: AnalysisService):
        self.db = db_manager
        self.analysis = analysis_service
        self.client = None
        self.model = config.CLAUDE_MODEL
        self._init_client()
    
    def _init_client(self):
        """初始化Claude客户端"""
        if anthropic is None:
            logger.warning("anthropic库未安装")
            return
        
        api_key = config.CLAUDE_API_KEY
        base_url = getattr(config, 'CLAUDE_BASE_URL', '')
        
        if api_key and api_key != "your_api_key_here":
            try:
                if base_url:
                    self.client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
                else:
                    self.client = anthropic.Anthropic(api_key=api_key)
                logger.info("Claude API客户端初始化成功")
            except Exception as e:
                logger.error(f"Claude API客户端初始化失败: {e}")
    
    def is_available(self) -> bool:
        """检查AI服务是否可用"""
        return self.client is not None
    
    def set_api_key(self, api_key: str, base_url: str = ""):
        """设置API Key和代理地址"""
        if anthropic is None:
            return False
        
        try:
            if base_url:
                self.client = anthropic.Anthropic(api_key=api_key, base_url=base_url)
            else:
                self.client = anthropic.Anthropic(api_key=api_key)
            self.base_url = base_url
            return True
        except Exception as e:
            logger.error(f"设置API Key失败: {e}")
            return False
    
    def start_session(self, student_id: int) -> str:
        """
        开始新的对话会话
        
        Returns:
            会话ID
        """
        session_id = str(uuid.uuid4())[:8]
        return session_id
    
    def chat(self, student_id: int, session_id: str, user_message: str) -> str:
        """
        发送对话消息
        
        Args:
            student_id: 学生数据库ID
            session_id: 会话ID
            user_message: 用户消息
            
        Returns:
            AI回复内容
        """
        if not self.is_available():
            return "AI服务不可用，请检查API Key配置。"
        
        # 保存用户消息
        self.db.add_conversation(AIConversation(
            student_id=student_id,
            session_id=session_id,
            role="user",
            message=user_message
        ))
        
        # 获取学生分析摘要
        student_summary = self.analysis.generate_student_summary(student_id)
        
        # 构建系统提示词
        system_prompt = CAREER_COUNSELOR_SYSTEM_PROMPT.format(
            student_analysis=student_summary
        )
        
        # 获取对话历史
        history = self.db.get_conversation_history(student_id, session_id)
        
        # 构建消息列表
        messages = []
        for conv in history:
            messages.append({
                "role": conv.role,
                "content": conv.message
            })
        
        try:
            # 调用Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=messages
            )
            
            assistant_message = response.content[0].text
            
            # 保存AI回复
            self.db.add_conversation(AIConversation(
                student_id=student_id,
                session_id=session_id,
                role="assistant",
                message=assistant_message
            ))
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"AI对话失败: {e}")
            return f"抱歉，对话出现错误: {str(e)}"
    
    def generate_career_report(self, student_id: int, session_id: str) -> Optional[CareerReport]:
        """
        生成职业规划报告 - 两阶段生成避免截断
        
        Args:
            student_id: 学生数据库ID
            session_id: 会话ID（用于获取对话上下文）
            
        Returns:
            CareerReport 或 None
        """
        if not self.is_available():
            logger.error("AI服务不可用")
            return None
        
        # 获取学生分析摘要
        student_summary = self.analysis.generate_student_summary(student_id)
        
        # 获取对话历史
        history = self.db.get_conversation_history(student_id, session_id)
        if not history:
            logger.warning(f"学生{student_id}会话{session_id}没有对话历史")
            return None
        
        conversation_summary = "\n".join([
            f"{'学生' if c.role == 'user' else 'AI'}: {c.message}"
            for c in history[-20:]  # 只取最近20条对话，避免太长
        ])
        
        # === 第一阶段：生成简洁的结构化数据 ===
        structure_prompt = f"""基于以下信息，提取学生的关键特质和推荐。

## 学生成绩
{student_summary}

## 对话摘要
{conversation_summary}

请输出简洁的JSON（每个字段不超过50字）：

{{
  "personality": ["特质1", "特质2", "特质3"],
  "subjects": ["科目1", "科目2", "科目3"],
  "careers": ["职业1", "职业2", "职业3"],
  "majors": ["专业1", "专业2", "专业3"]
}}

只输出JSON，不要其他文字。"""
        
        try:
            logger.info(f"为学生{student_id}生成职业规划报告 - 第一阶段")
            
            # 第一阶段：获取结构化数据
            response1 = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": structure_prompt}]
            )
            
            response_text = response1.content[0].text.strip()
            
            # 提取JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end <= json_start:
                logger.error("未找到JSON结构")
                return None
            
            json_str = response_text[json_start:json_end]
            
            try:
                structure_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                logger.error(f"JSON内容: {json_str}")
                return None
            
            # === 第二阶段：生成详细分析 ===
            logger.info("第二阶段：生成详细分析")
            
            analysis_prompt = f"""基于以下信息，写一份详细的职业规划分析报告（800-1000字）。

## 学生成绩
{student_summary}

## 对话内容
{conversation_summary}

## 初步结论
- 性格特质：{', '.join(structure_data.get('personality', []))}
- 推荐科目：{', '.join(structure_data.get('subjects', []))}
- 适合职业：{', '.join(structure_data.get('careers', []))}
- 推荐专业：{', '.join(structure_data.get('majors', []))}

请写一份完整的分析报告，包括：
1. 学生优势与特质分析
2. 选科建议及理由
3. 职业方向分析
4. 专业推荐与发展路径
5. 具体行动建议

用markdown格式，语言亲切专业。"""
            
            response2 = self.client.messages.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": analysis_prompt}]
            )
            
            detailed_analysis = response2.content[0].text.strip()
            
            # 构建报告对象
            report = CareerReport(
                student_id=student_id,
                personality_traits={
                    f"特质{i+1}": trait 
                    for i, trait in enumerate(structure_data.get('personality', ['待分析']))
                },
                subject_recommendations={
                    "推荐科目": structure_data.get('subjects', []),
                    "说明": "基于学生成绩和兴趣综合分析"
                },
                career_recommendations={
                    "适合职业": structure_data.get('careers', []),
                    "说明": "根据性格特质和学科优势推荐"
                },
                major_recommendations={
                    "推荐专业": structure_data.get('majors', []),
                    "说明": "适合学生特点的专业方向"
                },
                detailed_analysis=detailed_analysis
            )
            
            # 保存报告
            report_id = self.db.add_career_report(report)
            logger.info(f"报告保存成功，ID: {report_id}")
            
            return report
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}", exc_info=True)
            return None
    
    def get_quick_analysis(self, student_id: int) -> str:
        """
        获取快速分析（不需要对话）
        
        直接基于成绩数据给出初步建议
        """
        if not self.is_available():
            return "AI服务不可用"
        
        student_summary = self.analysis.generate_student_summary(student_id)
        
        prompt = f"""基于以下学生成绩分析，给出简短的学科选择建议（200字以内）：

{student_summary}

请直接给出建议，不要有其他客套话。"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"快速分析失败: {e}")
            return f"分析失败: {str(e)}"
