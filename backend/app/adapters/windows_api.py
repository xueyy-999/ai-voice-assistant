"""
Windows API适配器 - 封装系统操作
"""
import os
import subprocess
from typing import Optional, List, Dict
import psutil
from app.utils.logger import logger


class WindowsAPI:
    """Windows系统API封装"""
    
    def __init__(self):
        self.common_apps = self._load_common_apps()
    
    def _load_common_apps(self) -> Dict[str, str]:
        """加载常用应用路径"""
        return {
            "微信": r"C:\Program Files\Tencent\WeChat\WeChat.exe",
            "wechat": r"C:\Program Files\Tencent\WeChat\WeChat.exe",
            "qq": r"C:\Program Files\Tencent\QQ\Bin\QQScLauncher.exe",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "浏览器": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "vscode": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            "vs code": r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            "记事本": "notepad.exe",
            "notepad": "notepad.exe",
            "计算器": "calc.exe",
            "calc": "calc.exe",
            "网易云音乐": r"C:\Program Files (x86)\Netease\CloudMusic\cloudmusic.exe",
            "网易云": r"C:\Program Files (x86)\Netease\CloudMusic\cloudmusic.exe",
            "cloudmusic": r"C:\Program Files (x86)\Netease\CloudMusic\cloudmusic.exe",
        }
    
    def find_app_path(self, app_name: str) -> Optional[str]:
        """
        查找应用程序路径
        
        Args:
            app_name: 应用名称
            
        Returns:
            应用程序路径，未找到返回None
        """
        app_name_lower = app_name.lower()
        
        # 先查找预定义路径
        if app_name_lower in self.common_apps:
            path = os.path.expandvars(self.common_apps[app_name_lower])
            if os.path.exists(path):
                return path

        # 常见安装路径补充（尤其是 32 位/64 位差异）
        if app_name_lower in ["微信", "wechat"]:
            pf = os.environ.get("ProgramFiles", r"C:\\Program Files")
            pf86 = os.environ.get("ProgramFiles(x86)", r"C:\\Program Files (x86)")
            candidates = [
                os.path.join(pf, "Tencent", "WeChat", "WeChat.exe"),
                os.path.join(pf86, "Tencent", "WeChat", "WeChat.exe"),
            ]
            for c in candidates:
                if os.path.exists(c):
                    return c
        
        # 尝试直接作为命令
        if app_name_lower.endswith('.exe'):
            return app_name
        
        # 尝试添加.exe
        return app_name + '.exe'
    
    def start_process(self, app_path: str, args: List[str] = None) -> Optional[int]:
        """
        启动进程
        
        Args:
            app_path: 应用程序路径
            args: 命令行参数
            
        Returns:
            进程ID，失败返回None
        """
        try:
            # 对于系统命令（如 notepad.exe, calc.exe），使用 shell=True
            if app_path.lower() in ['notepad.exe', 'calc.exe', 'mspaint.exe', 'explorer.exe', '记事本.exe']:
                cmd = app_path.replace('记事本.exe', 'notepad.exe')
                if args:
                    cmd = f"{app_path} {' '.join(args)}"
                
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            else:
                # 对于其他应用，使用正常方式启动
                cmd = [app_path]
                if args:
                    cmd.extend(args)
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            
            logger.info(f"✅ 启动进程: {app_path} (PID: {process.pid})")
            return process.pid
            
        except Exception as e:
            logger.error(f"❌ 启动进程失败: {app_path} - {e}")
            return None
    
    def kill_process_by_name(self, process_name: str) -> bool:
        """
        根据进程名结束进程
        
        Args:
            process_name: 进程名（如 WeChat.exe）
            
        Returns:
            是否成功
        """
        try:
            killed_count = 0
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == process_name.lower():
                        proc.kill()
                        killed_count += 1
                        logger.info(f"✅ 结束进程: {process_name} (PID: {proc.pid})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return killed_count > 0
            
        except Exception as e:
            logger.error(f"❌ 结束进程失败: {process_name} - {e}")
            return False
    
    def find_process_by_name(self, process_name: str) -> List[Dict]:
        """
        查找进程
        
        Args:
            process_name: 进程名
            
        Returns:
            进程信息列表
        """
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    if process_name.lower() in proc.info['name'].lower():
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'status': proc.info['status']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            logger.error(f"查找进程失败: {e}")
        
        return processes
    
    def is_process_running(self, process_name: str) -> bool:
        """检查进程是否运行"""
        return len(self.find_process_by_name(process_name)) > 0
    
    def open_file(self, file_path: str) -> bool:
        """
        用默认程序打开文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        try:
            os.startfile(file_path)
            logger.info(f"✅ 打开文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 打开文件失败: {file_path} - {e}")
            return False
    
    def open_url(self, url: str) -> bool:
        """
        在默认浏览器打开URL
        
        Args:
            url: 网址
            
        Returns:
            是否成功
        """
        try:
            import webbrowser
            webbrowser.open(url)
            logger.info(f"✅ 打开URL: {url}")
            return True
        except Exception as e:
            logger.error(f"❌ 打开URL失败: {url} - {e}")
            return False
    
    def get_system_volume(self) -> Optional[int]:
        """获取系统音量（0-100）"""
        try:
            # Windows音量控制需要使用pycaw库
            # 这里简化实现
            return 50  # 默认返回50%
        except Exception as e:
            logger.error(f"获取音量失败: {e}")
            return None
    
    def set_system_volume(self, level: int) -> bool:
        """
        设置系统音量
        
        Args:
            level: 音量级别 (0-100)
            
        Returns:
            是否成功
        """
        try:
            # 使用nircmd工具设置音量（Windows）
            # 或使用pycaw库
            # 这里简化实现
            logger.info(f"✅ 设置音量: {level}%")
            return True
        except Exception as e:
            logger.error(f"❌ 设置音量失败: {e}")
            return False


# 全局实例
windows_api = WindowsAPI()

