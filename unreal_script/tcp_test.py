import socket

def server_tcp_accept():
    # 创建一个TCP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定的IP地址和端口
    server_ip = "10.0.210.25"
    server_port = 8888
    server_socket.bind((server_ip, server_port))
    # 开始监听，最大连接数为5
    server_socket.listen(5)
    print("服务器正在监听端口", server_port)
    try:
        # 接受客户端连接
        client_socket, client_address = server_socket.accept()
        print("收到来自", client_address, "的连接")
        # 接收客户端发送的数据
        data = client_socket.recv(1024).decode('utf-8')
        print("收到客户端消息:", data)
        # 发送回复给客户端
        response = "我已经收到你的消息".encode('utf-8')
        client_socket.send(response)
    except socket.error as e:
        print("服务器出错:", e)
    finally:
        # 关闭客户端套接字和服务器套接字
        client_socket.close()
        server_socket.close()




def client_tcp_connect():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_ip = "10.0.210.173"
    server_ip = "10.0.210.25"
    server_port = 8888

    try:
        client_socket.connect((server_ip, server_port))
        print("成功连接到服务器")

        # message = "dp.override iPhoneX"
        # message = "dp.override iPhone13ProMax"
        # message = "r.MobileContentScaleFactor"
        # message = "r.setres 1280x720f"
        # message = "sg.ResolutionQuality"
        # message = "r.ScreenPercentage 100"
        # message = "r.MobileContentScaleFactor 0"
        # message = "ios.PhysicalScreenDensity 401"
        message = "r.SceneRenderTargetResizeMethodForceOverride"
        message = "r.SceneRenderTargetResizeMethod"
        client_socket.send(message.encode('utf-8'))

        response = client_socket.recv(1024).decode('utf-8')
        print("收到服务器的回复:", response)
    except socket.error as e:
        print("连接服务器出错:", e)
    finally:
        client_socket.close()

if __name__ == "__main__":
    client_tcp_connect()





if __name__ == "__main__":
    server_tcp_accept()