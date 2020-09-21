import socket
import re
import gevent
import select


"""
1.epoll 有个特殊的内存空间，操作系统和应用程序公用，省去繁琐的复制消耗时间
2.列表不再使用遍历方式，而是使用事件通知方式（哪一个套接字的数据到了，操作系统就过去设置它可以收了）。
"""

def service_client(new_socket, request):
	"""为这个客户端返回数据"""
	# 1.接收浏览器发来的请求，即http请求
	# GET / HTTP/1.1
	# ......
	# request = new_socket.recv(1024).decode("utf-8")
	# print(">>>"*50)
	# print(request)
	
	request_lines = request.splitlines()  # 字符串进行分割后，返回值是一个列表
	print("")
	print(">>>"*50)
	print("request_lines = %s" % str(request_lines))  # 打印列表方法，将列表转换成字符
	
	print("")
	print("-"*20)
    # “request_lines[0]” 内容是 'GET /index.html HTTP/1.1' ，正则匹配到 GET /index.html
    ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
	print(ret)
	file_name = ""
	if ret:
		file_name = ret.group(1)  # 匹配到 /index.html
		#print("file_name = %s" % file_name)
		if file_name == "/":
			file_name = "/index.html"
		

	# 2.返回http格式的数据，给浏览器
	try:
		f = open("./html"+ file_name, "rb")
	except:
		response = "HTTP/1.1 404 NOT FONUD\r\n"
		response += "\r\n"
		response += "----------file not fonud---------"
		new_socket.send(response.encode("utf-8"))  # 以二进制发送
		
	else:	
		html_content = f.read()
		f.close()
		response_body = html_content

		# 2.1准备发送给浏览器的数据---header
		response_header = "HTTP/1.1 200 OK\r\n"
		response_header += "Content-Length:%d\r\n" % len(response_body)  # 告知浏览器发送数据包大小，以防止浏览器一直转圈圈等待。
		response_header += "\r\n"
		print("%s" % response_header)
		# 2.2准备发送给浏览器的数据--body
		# response += "hahahaha"
		# new_socket.send(response.encode("utf-8"))
		
		# 将response 发送给浏览器

		response = response_header.encode("utf-8") + response_body  # header 和 body 必须都是二进制才能相加
		new_socket.send(response)

	# 关闭套接字
	# new_socket.close() 


def main():
	"""用来完成整体的控制"""
	# 1.创建套接字
	tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置当服务器先调用close() 及服务器4次挥手后资源能够立即释放。这就保证下次运行程序，可立即监听服务端口。
	tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
	
	# 2.绑定
	tcp_server_socket.bind(("", 8080))

	# 3.变为监听套接字
	tcp_server_socket.listen(128)
	tcp_server_socket.setblocking(False)  # 将套接字变为非堵塞

	# 创建一个epoll对象及创建共享内存
	epl = select.epoll()
	
	# 将监听套接字对应的fd注册到epoll中，检测到有数据输入
	epl.register(tcp_server_socket.fileno(), select.EPOLLIN)

	fd_event_dict = dict()  # 由于client_socket 这个套接字此时不存在，因此采用字典方式记录不同客户端的套接字

	while True:
    """
    1. tcp_server_socket.fileno() = new_socket 及有新客户接入，才会产生这个值。第一次调用后，会再次处于堵塞状态，也就是监听状态。
    2. fd_event_dict[fd] = client_socket: 及已存在客户端及其对应的socket信息
    3. epl.poll()是事件列表
    """
		
		fd_event_list = epl.poll()  # 默认会堵塞，直到 os监测到数据到来 通过事件通知方式 告诉这个程序，此时才会解堵塞
		print ("%s" % str(epl.poll()))
		# [(fd, event), (套接字对应的文件描述符， 这个文件描述符到底是什么事件 例如 可以调用recv接收等)]
		for fd, event in fd_event_list:
        """
        收到事件通知，存在两种情况
        1. 新的客户连接，tcp_server_socket.fileno()会产生一个值，通过判断时间列表里的fd 是否等于这个值来判断是否是新的客户接入
        2. 已连接客户发来消息，通过判断如果不是新客户连接，那就是已有客户发来的消息
        """
			if fd == tcp_server_socket.fileno():
                # 判断是否是新客户接入
				new_socket, client_addr = tcp_server_socket.accept()
				epl.register(new_socket.fileno(), select.EPOLLIN)
				fd_event_dict[new_socket.fileno()] = new_socket
			elif event == select.EPOLLIN:
				# 判断已经连接的客户端是否有数据发送过来
				recv_data = fd_event_dict[fd].recv(1024).decode("utf-8")
				if recv_data:
					service_client(fd_event_dict[fd], recv_data)
				else:
					fd_event_dict[fd].close()
					eql.unregister(fd)  # 删除共享内存里收到对应null的套接字
					del fd_event_dict[fd]  # 删除字典里 对应的收到null 的套接字
					
		# 5.为这个客户的服务
		#p = threading.Thread(target=service_client, args=(new_socket, ))
		#p.start()
		# service_client(new_socket)
		#new_socket.close()
	        #gevent.spawn(service_client, new_socket)

	# 6.关闭监听套接字
	tcp_server_socket.close()


if __name__ == "__main__":
	main()
