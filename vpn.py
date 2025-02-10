import os
import platform
import subprocess
import requests
import psutil
import winreg  # 仅Windows需要
from socket import gethostbyname, gaierror

# 配置部分
CHECK_IP_SERVICE = "https://ipinfo.io/json"  # IP检测服务
VPN_ASN_KEYWORDS = ['VPN', 'PROXY', 'TOR']  # VPN服务商的ASN特征关键词
VPN_PROCESS_NAMES = ['openvpn', 'wireguard', 'nordvpn', 'expressvpn', 'proxyman']  # 常见VPN客户端进程名
VPN_INTERFACES = ['tun0', 'tun1', 'ppp0', 'ppp1', 'wg0', 'utun']  # 常见VPN接口名称

def check_system_proxy():
    """检测系统代理设置"""
    proxies = {
        'http': os.environ.get('http_proxy'),
        'https': os.environ.get('https_proxy')
    }
    if any(proxies.values()):
        return True, "系统环境变量设置了代理"
    
    # Windows注册表检测
    if platform.system() == 'Windows':
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                               r'Software\Microsoft\Windows\CurrentVersion\Internet Settings') as key:
                if winreg.QueryValueEx(key, 'ProxyEnable')[0] == 1:
                    return True, "Windows系统启用了代理服务器"
        except Exception:
            pass
    
    return False, "未检测到系统代理设置"

def check_network_interfaces():
    """检测VPN虚拟接口"""
    interfaces = psutil.net_if_addrs().keys()
    for iface in interfaces:
        if any(vpn_if in iface.lower() for vpn_if in VPN_INTERFACES):
            return True, f"检测到VPN网络接口: {iface}"
    return False, "未检测到VPN专用接口"

def check_vpn_processes():
    """检测正在运行的VPN进程"""
    for proc in psutil.process_iter(['name']):
        if any(keyword in proc.info['name'].lower() for keyword in VPN_PROCESS_NAMES):
            return True, f"检测到VPN进程: {proc.info['name']}"
    return False, "未检测到VPN客户端进程"

def check_ip_metadata():
    """通过IP元数据检测"""
    try:
        resp = requests.get(CHECK_IP_SERVICE, timeout=5)
        data = resp.json()
        
        # 检测IP类型
        if data.get('privacy', {}).get('vpn') or data.get('proxy', {}).get('proxy'):
            return True, "IP地址被标记为VPN/代理"
            
        # 检测ASN信息
        asn = data.get('org', '').upper()
        if any(keyword in asn for keyword in VPN_ASN_KEYWORDS):
            return True, f"IP归属ASN可能为VPN服务商: {asn}"
            
        return False, f"公网IP: {data.get('ip')} ({data.get('country')})"
    except Exception as e:
        return False, f"IP检测失败: {str(e)}"

def comprehensive_check():
    """综合检测"""
    results = []
    
    # 检测系统代理
    proxy_status, proxy_msg = check_system_proxy()
    results.append(("系统代理", proxy_status, proxy_msg))
    
    # 检测网络接口
    interface_status, interface_msg = check_network_interfaces()
    results.append(("网络接口", interface_status, interface_msg))
    
    # 检测VPN进程
    process_status, process_msg = check_vpn_processes()
    results.append(("运行进程", process_status, process_msg))
    
    # 检测IP信息
    ip_status, ip_msg = check_ip_metadata()
    results.append(("IP元数据", ip_status, ip_msg))
    
    return results

def print_results(results):
    """可视化输出结果"""
    print("\n" + "="*40 + " 网络状态检测 " + "="*40)
    for category, status, msg in results:
        status_str = "[!] 检测到异常" if status else "[√] 状态正常"
        print(f"{category.ljust(10)} {status_str} | {msg}")
    print("="*94 + "\n")

if __name__ == '__main__':
    # 执行综合检测
    detection_results = comprehensive_check()
    print_results(detection_results)
    
    # 综合判断
    total_risk = sum([status for _, status, _ in detection_results])
    if total_risk > 0:
        print("警告：可能正在使用代理/VPN")
    else:
        print("没开代理/VPN")