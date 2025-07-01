#!/usr/bin/env python3

import rospy
import os
import sys
import time
import random
from pynput import keyboard
from threading import Thread, Event, Lock
import threading
import cv2
import numpy as np
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
from playsound import playsound


from aiui.srv import TTS, TTSRequest
from aiui.srv import VLMProcess, VLMProcessRequest
from aiui.srv import StringService, StringServiceRequest
from aiui.srv import DH5SetPosition, DH5SetPositionRequest
from aiui.srv import VLAProcess, VLAProcessRequest
from aiui.srv import CheckRunStatus, CheckRunStatusRequest, CheckRunStatusResponse
from sentenceBuffer import SentenceBuffer


class ExtendedKeyboardActionNode:
    def __init__(self):
        # 初始化ROS节点（仅用于报告状态）
        rospy.init_node('extended_keyboard_action_printer', anonymous=True)
        self.arm_client = rospy.ServiceProxy("aris_node/cmd_str_srv",StringService)
        self.sys_client = rospy.ServiceProxy("aris_node/sys_str_srv",StringService)
        self.vlm_client = rospy.ServiceProxy("vlm_service",VLMProcess)
        self.tts_client = rospy.ServiceProxy("/tts_service/player",TTS)
        self.dh5_client = rospy.ServiceProxy("/dh5/set_all_position",DH5SetPosition)
        self.vla_client = rospy.ServiceProxy("vla_service", VLAProcess)
        self.check_client = rospy.ServiceProxy("/aris_node/check_srv", CheckRunStatus)
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
        # 清屏并设置初始颜色
        os.system('clear')  # Linux下清屏命令
        print("\033[1;36m")  # 设置颜色为青色
        print("      人形机器人意图菜单")
        print("==============================")
        print("\033[0m")  # 重置颜色
        print(f"节点名称: {rospy.get_name()}")
        print("功能: 通过键盘触发机器人行为意图")
        print("按以下键执行相应动作：\n")
        
        # 定义丰富的颜色方案
        colors = [
            "\033[1;31m",  # 红色
            "\033[1;32m",  # 绿色
            "\033[1;33m",  # 黄色
            "\033[1;34m",  # 蓝色
            "\033[1;35m",  # 紫色
            "\033[1;36m",  # 青色
            "\033[1;37m",  # 白色
        ]
        """
        if key_char == '2':         self.handle_detected_intent("Nod")
        elif key_char == '3':       self.handle_detected_intent("SayHi")
        elif key_char == '4':       self.handle_detected_intent("handshake")
        elif key_char == '5':       self.handle_detected_intent("Bow")
        elif key_char == '6':       self.handle_detected_intent("Good")
        elif key_char == '7':       self.handle_detected_intent("take_photo")
        elif key_char == '8':       self.handle_detected_intent("handclap")
        elif key_char == '9':       self.handle_detected_intent("LOVE")
        elif key_char == 'p':       self.handle_detected_intent("pangu")
        elif key_char == 'a':       self.handle_detected_intent("vla")
        elif key_char == 'm':       self.handle_detected_intent("vlm")
        elif key_char == '0':  # 0键用于退出
        """
        
        # 动作列表（三列布局）
        actions = [
            ("2", "👍 点头介绍(Nod)"),
            ("3", "👋 打招呼(SayHi)"),
            ("4", "🤝 握手(handshake)"),
            ("5", "🙇 鞠躬(Bow)"),
            ("6", "🤳 自拍(pose)"),
            ("7", "📷 拍照(take_photo)"),
            ("8", "👏 鼓掌(handclap)"),
            ("9", "💖 比心(LOVE)"),
            ("p", "📖 盘古故事(pangu)"),
            ("a", "👁️‍🗨️ 视觉语言动作(vla)"),
            ("m", "🖼️ 视觉描述(vlm)"),
            ("0", "🚪 退出程序"),
            ("e", "🔋 使能(enable)"),
            ("d", "💀 掉电(disable)"),
        ]
        
        # 计算每列需要显示的数量（三列）
        col_count = 3
        per_col = (len(actions) + col_count - 1) // col_count
        
        # 按列打印动作
        for i in range(per_col):
            row = []
            for j in range(col_count):
                idx = i + j * per_col
                if idx < len(actions):
                    action = actions[idx]
                    color_idx = (i * col_count + j) % len(colors)
                    row.append(f"{colors[color_idx]}[{action[0]}]\033[0m {action[1]}")
                else:
                    row.append("")
            # 打印一行三列
            print(" | ".join(f"{item:<30}" for item in row))
        
        # 添加操作说明
        print("\n\033[1;33m当前实时动作反馈\033[0m")
        print("\033[1;31m提示：按任意动作键触发相应意图！\033[0m")
        print("\033[1;34m退出：按 0 或 Ctrl+C 退出程序\033[0m\n")
        print("\033[1;35m* 部分动作有随机效果（握手、鞠躬等会有不同表现）\033[0m")
        print("\033[1;36m* 拍照功能会同时触发动作和相机操作\033[0m")
    def handle_detected_intent(self, intent):
        
        
        if intent == "SayHi":
            rospy.loginfo(f"检测到 [{intent}] 意图, 执行打招呼动作")
            tts_req = TTSRequest()
            tts_req.request = "你好呀，欢迎您来到南方科技大学机器人研究院，很高兴见到您！"
            # self.tts_client.wait_for_service()
            Thread(target=self.tts_client.call, args=(tts_req,), daemon=True).start()
            req = StringServiceRequest()
            req.request = 3
            # self.arm_client.wait_for_service()
            Thread(target=self.arm_client.call, args=(req,), daemon=True).start()

        elif intent == "handshake":
            rospy.loginfo(f"检测到 [{intent}] 意图, 执行握手动作")
            tts_req = TTSRequest()
            tts_req.request = "好呀，和我握个手吧，很高兴认识你，我还想再多和你交流交流呢！"
            # self.tts_client.wait_for_service()
            Thread(target=self.tts_client.call, args=(tts_req,), daemon=True).start()
            req = StringServiceRequest()
            req.request = 4 # TODO
            # self.arm_client.wait_for_service()
            Thread(target=self.arm_client.call, args=(req,), daemon=True).start()
        elif intent == "Bow":
            rospy.loginfo(f"检测到 [{intent}] 意图, 执行鞠躬欢送动作")
            tts_req = TTSRequest()
            tts_req.request = "哇时间过得好快, 再见喽，期待下次再和您见面，记得要常来看我哦！"
            # self.tts_client.wait_for_service()
            Thread(target=self.tts_client.call, args=(tts_req,), daemon=True).start()
            req = StringServiceRequest()
            req.request = 5 # TODO
            # self.arm_client.wait_for_service()
            Thread(target=self.arm_client.call, args=(req,), daemon=True).start()

 
        elif intent == "Nod":
            print(f"检测到 [{intent}] 意图, 执行点头动作")
            tts_req = TTSRequest()
            tts_req.request = "我叫南科盘古，我是南方科技大学机器人研究院研发的第一款人形机器人，我可以做一些简单的交互动作，还可以陪你闲聊散心, 另外我还是实验室的科研小助手，想知道今天的天气也可以问我哦！"
            # self.tts_client.wait_for_service()
            Thread(target=self.tts_client.call, args=(tts_req,), daemon=True).start()
            
            # req = StringServiceRequest()
            # req.request = '2' # TODO
            # self.arm_client.wait_for_service()
            # self.arm_client.call(req)
            # Thread(target=self.arm_client.call, args=(req,), daemon=True).start()
        
        elif intent == "vla":
            rospy.loginfo(f"检测到 [{intent}] 意图, 执行视觉语言动作")
            tts_req = TTSRequest()
            tts_req.request = "好的，请稍等片刻"
            # self.tts_client.wait_for_service()
            Thread(target=self.tts_client.call, args=(tts_req,), daemon=True).start()

            vla_req = VLAProcessRequest()
            vla_req.prompt = "帮我拿一下这个瓶子"
            # self.vla_client.wait_for_service()
            Thread(target=self.vla_client.call, args=(vla_req,), daemon=True).start()
        
        elif intent == "vlm":
            rospy.loginfo(f"检测到 [{intent}] 意图, 执行描述动作")
            tts_req = TTSRequest()
            tts_req.request = "好的，让我仔细看一下！"
            # self.tts_client.wait_for_service()
            Thread(target=self.tts_client.call, args=(tts_req,), daemon=True).start()

            vlm_req = VLMProcessRequest()
            vlm_req.prompt = "请描述一下看到了什么"
            # self.vlm_client.wait_for_service()
            resp = self.vlm_client.call(vlm_req)
            vlm_result = resp.vlm_result
            rospy.loginfo(f"VLM 结果: {vlm_result}")

        elif intent == "pose":
            self.intent_state = True
            rospy.loginfo(f"检测到 [{intent}] 意图, 执行自拍动作")
            tts_req = TTSRequest()
            tts_req.request = "好的，摆个点赞的姿势，来和我自拍一张吧"
            # self.tts_client.wait_for_service()
            Thread(target=self.tts_client.call, args=(tts_req,), daemon=True).start()
            arm_req = StringServiceRequest()
            arm_req.request = random.choice([6, 9, 10])
            # self.arm_client.wait_for_service()
            Thread(target=self.arm_client.call, args=(arm_req,), daemon=True).start()

        elif intent == "pangu":
            self.intent_state = True
            rospy.loginfo(f"检测到 [{intent}] 意图, 讲述盘古开天地的故事")
            tts_req = TTSRequest()
            tts_req.request = "好的，盘古是中国古代传说时期中开天辟地的神。在很久很久以前，宇宙混沌一团，盘古凭借着自己的神力把天地开辟出来了。"
            # self.tts_client.wait_for_service()
            Thread(target=self.tts_client.call, args=(tts_req,), daemon=True).start()
            
        elif intent == "take_photo":
            self.intent_state = True
            rospy.loginfo(f"检测到 [{intent}] 意图, 执行拍照动作")
            tts_req = TTSRequest()
            tts_req.request = "好的，没问题，大家都过来吧！站  到我面前，让我来为大家拍一张大合照！"
            # self.tts_client.wait_for_service()
            Thread(target=self.tts_client.call, args=(tts_req,), daemon=True).start()
            arm_req = StringServiceRequest()
            arm_req.request = 7
            # self.arm_client.wait_for_service()
            Thread(target=self.arm_client.call, args=(arm_req,), daemon=True).start()
            
            self.thake_photo()
        elif intent == "LOVE":
            rospy.loginfo(f"检测到 [{intent}] 意图, 执行比心动作")
            tts_req = TTSRequest()
            tts_req.request = "南科大爱你呦！啾咪啾咪！"
            # self.tts_client.wait_for_service()
            Thread(target=self.tts_client.call, args=(tts_req,), daemon=True).start()
            arm_req = StringServiceRequest()
            arm_req.request = random.choice([12, 13])
            # self.arm_client.wait_for_service()
            Thread(target=self.arm_client.call, args=(arm_req,), daemon=True).start()
        
        elif intent == "handclap":  
            rospy.loginfo(f"检测到 [{intent}] 意图, 执行鼓掌动作")
            tts_req = TTSRequest()
            tts_req.request = "精彩精彩！大家一起鼓掌！太棒了！"
            # self.tts_client.wait_for_service()
            Thread(target=self.tts_client.call, args=(tts_req,), daemon=True).start()
            arm_req = StringServiceRequest()
            arm_req.request = 8
            # self.arm_client.wait_for_service()
            Thread(target=self.arm_client.call, args=(arm_req,), daemon=True).start()

    def thake_photo(self):
        bridge = CvBridge()
    
        try:
            rospy.sleep(0.8)
            self.play_existing_audio("/home/whc/aiui_ws/src/aiui/audio/look_at_me.mp3")
            # rospy.sleep(2)
            self.play_existing_audio("/home/whc/aiui_ws/src/aiui/audio/get_ready.mp3")
            # rospy.sleep(2)
            self.play_existing_audio("/home/whc/aiui_ws/src/aiui/audio/pose.mp3")
            # rospy.sleep(2)
            self.play_existing_audio("/home/whc/aiui_ws/src/aiui/audio/three.mp3")
            rospy.sleep(1.5)
            self.play_existing_audio("/home/whc/aiui_ws/src/aiui/audio/two.mp3")
            rospy.sleep(1.5)
            self.play_existing_audio("/home/whc/aiui_ws/src/aiui/audio/one.mp3")
            rospy.sleep(2.5)
            self.play_existing_audio("/home/whc/aiui_ws/src/aiui/audio/qie_zi.mp3")
            # rospy.sleep(2)

            
            # 等待并获取ROS图像消息
            rospy.loginfo("等待相机图像消息...")
            image_msg = rospy.wait_for_message("/camera/color/image_raw", Image, timeout=5.0)
            
            # 将ROS图像消息转换为OpenCV格式
            cv_image = bridge.imgmsg_to_cv2(image_msg, "bgr8")
            rospy.loginfo("成功获取图像!")
            
            # 保存图像
            cv2.imwrite("captured_image.jpg", cv_image)
            rospy.loginfo("图像已保存为 captured_image.jpg")
            
            # 创建全屏窗口显示图像
            screen_width, screen_height = 1920, 1080  # 根据实际屏幕分辨率调整
            window_name = "Fullscreen Image"
            cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
            # 调整图像尺寸以适应屏幕（保持宽高比）
            h, w = cv_image.shape[:2]
            scale = min(screen_width/w, screen_height/h)
            resized_image = cv2.resize(cv_image, (int(w*scale), int(h*scale)))
            
            # 创建黑色背景并在中央显示图像
            display_image = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
            x_offset = (screen_width - resized_image.shape[1]) // 2
            y_offset = (screen_height - resized_image.shape[0]) // 2
            display_image[y_offset:y_offset+resized_image.shape[0], 
                        x_offset:x_offset+resized_image.shape[1]] = resized_image
            
            # 显示图像
            cv2.imshow(window_name, display_image)
            rospy.loginfo("按任意键退出全屏显示...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        except rospy.ROSException:
            rospy.logerr("等待图像消息超时，请检查相机是否已启动")
        except Exception as e:
            rospy.logerr(f"发生错误: {str(e)}")

    def on_key_press(self, key):
        """键盘按下事件处理"""
        try:
            key_char = key.char
        except AttributeError:
            return  # 忽略特殊键
        self.check_client.wait_for_service()
        resp = self.check_client.call(CheckRunStatusRequest())
        if resp.ros_run_flag is True:
            rospy.loginfo("动作执行中，请稍候...")
            return
        
        # 处理按键 - 支持数字和字母键
        if key_char == '2':         self.handle_detected_intent("Nod")
        elif key_char == '3':       self.handle_detected_intent("SayHi")
        elif key_char == '4':       self.handle_detected_intent("handshake")
        elif key_char == '5':       self.handle_detected_intent("Bow")
        elif key_char == '6':       self.handle_detected_intent("pose")
        elif key_char == '7':       self.handle_detected_intent("take_photo")
        elif key_char == '8':       self.handle_detected_intent("handclap")
        elif key_char == '9':       self.handle_detected_intent("LOVE")
        elif key_char == 'p':       self.handle_detected_intent("pangu")
        elif key_char == 'a':       self.handle_detected_intent("vla")
        elif key_char == 'm':       self.handle_detected_intent("vlm")
        elif key_char == 'e':       
            req = StringServiceRequest()
            req.request = 2  # 鼓掌动作
            self.sys_client.wait_for_service()
            self.sys_client.call(req)
        elif key_char == 'd':
            req = StringServiceRequest()
            req.request = 3
            self.sys_client.wait_for_service()
            self.sys_client.call(req)
        elif key_char == '0':  # 0键用于退出
            print("\n\033[1;31m>>> 接收到退出命令，关闭节点...\033[0m")
            self.listener_running = False
            rospy.signal_shutdown("用户退出")
        time.sleep(0.8)  # 显示效果
        self.display_menu()  # 重新显示菜单

    
    
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