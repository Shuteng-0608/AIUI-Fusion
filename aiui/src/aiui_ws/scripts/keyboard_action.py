#!/usr/bin/env python3

import rospy
import os
import sys
import time
import threading
import random
from pynput import keyboard

class ExtendedKeyboardActionNode:
    def __init__(self):
        # 初始化ROS节点（仅用于报告状态）
        rospy.init_node('extended_keyboard_action_printer', anonymous=True)
        
        # 设置退出信号处理
        rospy.on_shutdown(self.shutdown_hook)
        
        # 键盘监听器线程控制
        self.listener_running = True
        self.listener = None
        
        # 显示初始菜单
        self.display_menu()
        
        # 启动键盘监听器线程
        self.start_keyboard_listener()
        
        rospy.loginfo(f"扩展键盘动作监听器已启动 (节点: {rospy.get_name()})")

    def display_menu(self):
        """清除终端并显示选项菜单"""
        os.system('clear')  # Linux下清屏命令
        print("\033[1;36m")  # 设置颜色为青色
        print("      扩展键盘动作监听器")
        print("==============================")
        print("\033[0m")  # 重置颜色
        print(f"节点名称: {rospy.get_name()}")
        print("功能: 监听键盘输入并显示相应动作")
        print("按以下键执行相应动作：\n")
        
        # 使用更丰富的颜色方案
        colors = [
            "\033[1;31m",  # 红色
            "\033[1;32m",  # 绿色
            "\033[1;33m",  # 黄色
            "\033[1;34m",  # 蓝色
            "\033[1;35m",  # 紫色
        ]
        
        # 动作列表（两列布局）
        actions = [
            ("1", "👏 鼓掌"),
            ("2", "✋ 举手"),
            ("3", "👋 再见"),
            ("4", "🤗 拥抱"),
            ("5", "🎤 唱歌"),
            ("6", "💃 跳舞"),
            ("7", "🎁 送礼"),
            ("8", "😄 大笑"),
            ("9", "🤔 思考"),
            ("a", "🤖 机器人舞"),
            ("b", "📸 拍照"),
            ("c", "🎉 庆祝"),
            ("0", "🚪 退出程序")
        ]
        
        # 分两列打印动作
        mid = (len(actions) + 1) // 2
        for i in range(mid):
            left_idx = i
            right_idx = i + mid
            
            # 左侧动作
            left_str = f"{colors[left_idx % len(colors)]}[{actions[left_idx][0]}]\033[0m  {actions[left_idx][1]}"
            
            # 右侧动作（如果存在）
            if right_idx < len(actions):
                right_str = f"{colors[right_idx % len(colors)]}[{actions[right_idx][0]}]\033[0m  {actions[right_idx][1]}"
            else:
                right_str = ""
            
            # 打印一行两个动作
            print(f"{left_str.ljust(25)}{right_str}")
        
        print("\n\033[1;31m当前正在监听键盘输入...\033[0m")
        print("\033[1;34mCtrl+C 或按0退出程序\033[0m\n")
        print("\033[1;35m提示：按任意动作键触发相应效果！\033[0m")

    def on_key_press(self, key):
        """键盘按下事件处理"""
        try:
            key_char = key.char
        except AttributeError:
            return  # 忽略特殊键
        
        # 处理按键 - 支持数字和字母键
        if key_char == '1':
            self.execute_action("鼓掌", self.clap_hands)
        elif key_char == '2':
            self.execute_action("举手", self.raise_hand)
        elif key_char == '3':
            self.execute_action("再见", self.wave_goodbye)
        elif key_char == '4':
            self.execute_action("拥抱", self.hug)
        elif key_char == '5':
            self.execute_action("唱歌", self.sing_song)
        elif key_char == '6':
            self.execute_action("跳舞", self.dance)
        elif key_char == '7':
            self.execute_action("送礼", self.give_gift)
        elif key_char == '8':
            self.execute_action("大笑", self.laugh_out_loud)
        elif key_char == '9':
            self.execute_action("思考", self.deep_thought)
        elif key_char == 'a':
            self.execute_action("机器人舞", self.robot_dance)
        elif key_char == 'b':
            self.execute_action("拍照", self.take_photo)
        elif key_char == 'c':
            self.execute_action("庆祝", self.celebrate)
        elif key_char == '0':  # 0键用于退出
            print("\n\033[1;31m>>> 接收到退出命令，关闭节点...\033[0m")
            self.listener_running = False
            rospy.signal_shutdown("用户退出")

    def execute_action(self, action_name, action_func):
        """执行并打印动作"""
        # 清除当前操作行
        print("\033[2K", end="")  # 清除当前行
        print(f"\033[1;32m>>> 执行动作: {action_name}\033[0m")
        
        # 调用具体动作函数
        action_func()
        
        time.sleep(0.8)  # 显示效果
        self.display_menu()  # 重新显示菜单
    
    # ============== 具体动作实现 ==============
    
    def clap_hands(self):
        """鼓掌动作"""
        for _ in range(3):
            time.sleep(0.2)
            print("\033[33m👏\033[0m", end="", flush=True)
        print("\n\033[1;33m掌声响起! 太棒了!\033[0m")
    
    def raise_hand(self):
        """举手动作"""
        # 添加举手的动画
        print("\n举手动作开始...")
        for step in ["低", "中", "高"]:
            time.sleep(0.3)
            print(f"\033[34m✋ 手举到{step}度\033[0m")
        print("\033[1;34m✋ 手已高高举起!\033[0m")
    
    def wave_goodbye(self):
        """再见动作"""
        print("\n挥手告别...")
        for i in range(5):
            time.sleep(0.2)
            print("\033[35m👋\033[0m", end="", flush=True)
        print("\n\033[1;35m再见朋友! 下次再见!\033[0m")
    
    def hug(self):
        """拥抱动作"""
        print("\n\033[33m张开双臂\033[0m")
        time.sleep(0.5)
        print("\033[33m🤗 给一个大大的拥抱!\033[0m")
        time.sleep(0.5)
        print("\033[33m💕 感受到温暖了吗?\033[0m")
    
    def sing_song(self):
        """唱歌动作"""
        print("\n🎵 准备唱歌...")
        for i in range(1, 4):
            print(f"\033[1;35m🎤 演唱第{i}段...\033[0m")
            time.sleep(0.5)
        lyrics = ["♪ 哆", "♪ 来", "♪ 咪", "♪ 发", "♪ 嗦", "♪ 拉", "♪ 西"]
        for note in lyrics:
            print(f"\033[1;35m{note}\033[0m", end=" ", flush=True)
            time.sleep(0.2)
        print("\n\033[1;36m🎶 演唱结束，掌声在哪里?\033[0m")
    
    def dance(self):
        """跳舞动作"""
        print("\n准备跳舞...")
        dance_moves = ["💃 旋转", "🕺 摇摆", "💃 跳跃", "🕺 滑步"]
        for move in dance_moves:
            print(f"\033[1;36m{move}\033[0m", end=" → ", flush=True)
            time.sleep(0.4)
        print("\n\033[1;33m✨ 舞蹈完美结束!\033[0m")
    
    def give_gift(self):
        """送礼动作"""
        gifts = ["🎁 神秘礼物", "💐 一束鲜花", "🎂 美味蛋糕", "📦 惊喜盒子"]
        gift = random.choice(gifts)
        print("\n\033[1;35m正在准备礼物...\033[0m")
        time.sleep(0.8)
        print(f"\033[1;35m🎀 包装精美的礼物\033[0m")
        time.sleep(0.5)
        print(f"\033[1;32m{gift} 送给你!\033[0m")
        print("\033[1;33m❤️ 希望你喜欢!\033[0m")
    
    def laugh_out_loud(self):
        """大笑动作"""
        print("\n\033[1;31m哈哈哈\033[0m ", end="")
        time.sleep(0.3)
        print("\033[1;32m呵呵呵\033[0m ", end="")
        time.sleep(0.3)
        print("\033[1;33m嘻嘻嘻\033[0m")
        time.sleep(0.3)
        print("\033[1;34m🤣 笑得停不下来了!\033[0m")
        time.sleep(0.5)
        print("\033[1;35m😆 太有趣了!!!\033[0m")
    
    def deep_thought(self):
        """思考动作"""
        print("\n\033[1;34m进入深度思考状态...\033[0m")
        for i in range(5):
            time.sleep(0.6)
            print("\033[34m💭\033[0m", end="", flush=True)
        print("\n\033[1;36m🤔 灵光一现! 我明白了!\033[0m")
    
    def robot_dance(self):
        """机器人舞动作"""
        print("\n启动机器人模式...")
        moves = [
            "⬆️ 抬右臂", 
            "⬇️ 放右臂", 
            "⬆️ 抬左臂", 
            "⬇️ 放左臂",
            "⏫ 跳跃", 
            "↩️ 旋转"
        ]
        for i, move in enumerate(moves, 1):
            time.sleep(0.4)
            print(f"\033[1;35m🤖 动作{i}: {move}\033[0m")
        print("\033[1;36m🤖 机器人舞蹈完成! 哔哔哔~\033[0m")
    
    def take_photo(self):
        """拍照动作"""
        print("\n\033[1;32m调整相机角度...\033[0m")
        time.sleep(0.5)
        print("\033[1;32m📷 准备就绪! 微笑!\033[0m")
        for i in range(3, 0, -1):
            time.sleep(0.8)
            print(f"\033[1;31m倒计时: {i}\033[0m")
        print("\033[1;33m📸 咔嚓! 完美照片诞生!\033[0m")
    
    def celebrate(self):
        """庆祝动作"""
        print("\n准备庆祝活动...")
        for _ in range(3):
            print("\033[1;35m🎊\033[0m", end=" ", flush=True)
            time.sleep(0.3)
        print("\n\033[1;36m🎉 庆祝时间到!!!\033[0m")
        time.sleep(0.5)
        print("\033[1;33m✨ 恭喜达成目标! ✨\033[0m")
    
    # ============== 线程管理 ==============
    
    def start_keyboard_listener(self):
        """启动键盘监听器线程"""
        self.keyboard_thread = threading.Thread(target=self.keyboard_listener_thread)
        self.keyboard_thread.daemon = True
        self.keyboard_thread.start()
        rospy.loginfo("键盘监听器线程已启动")

    def keyboard_listener_thread(self):
        """键盘监听器线程函数"""
        try:
            while self.listener_running and not rospy.is_shutdown():
                with keyboard.Listener(on_press=self.on_key_press) as listener:
                    self.listener = listener
                    listener.join()
        except Exception as e:
            rospy.logerr(f"键盘监听错误: {e}")
        finally:
            rospy.loginfo("键盘监听器线程已停止")

    def shutdown_hook(self):
        """节点关闭时的清理工作"""
        rospy.loginfo("正在关闭键盘动作监听器...")
        self.listener_running = False
        if self.listener:
            self.listener.stop()
        print("\n\033[1;34m扩展键盘动作监听器已安全关闭!\033[0m")
        print("\033[1;35m感谢使用! 下次再见! 👋\033[0m\n")

    def run(self):
        """主运行循环"""
        try:
            # 保持运行直到关闭
            while not rospy.is_shutdown() and self.listener_running:
                rospy.sleep(0.1)  # 轻微睡眠以减少CPU使用
        except rospy.ROSInterruptException:
            rospy.loginfo("ROS中断，关闭节点")

if __name__ == "__main__":
    try:
        node = ExtendedKeyboardActionNode()
        node.run()
    except rospy.ROSInterruptException:
        print("ROS中断异常")
    except Exception as e:
        rospy.logerr(f"程序发生错误: {e}")
    finally:
        print("程序结束")