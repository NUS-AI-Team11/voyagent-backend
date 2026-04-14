#!/usr/bin/env python
"""
VoyageAgent - 智能旅行规划系统
主入口点
"""

import logging
import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestrator.workflow import TravelPlanningWorkflow


def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('voyagent.log')
        ]
    )


def main():
    """主函数"""
    setup_logging()
    
    print("\n" + "=" * 60)
    print("🌍 欢迎使用 VoyageAgent - 智能旅行规划系统")
    print("=" * 60 + "\n")
    
    # 创建工作流
    workflow = TravelPlanningWorkflow()
    
    # 获取用户输入
    print("请输入您的旅行需求（支持多行输入，输入 'END' 结束）：\n")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        lines.append(line)
    
    user_input = '\n'.join(lines)
    
    if not user_input.strip():
        print("❌ 输入为空，退出程序")
        return
    
    # 执行工作流
    try:
        context = workflow.run(user_input)
        
        # 显示结果
        if context.final_handbook:
            print("\n✅ 规划成功！")
            print(f"📋 旅行手册: {context.final_handbook.title}")
        else:
            print("\n⚠️ 规划过程中出现问题")
            if context.errors:
                print("错误信息:")
                for error in context.errors:
                    print(f"  - {error}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断程序")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序出错: {str(e)}")
        logging.exception("未处理的异常")
        sys.exit(1)


if __name__ == "__main__":
    main()
