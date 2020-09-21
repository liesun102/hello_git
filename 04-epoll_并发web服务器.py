import socket
import re
import gevent
import select


"""
1.epoll �и�������ڴ�ռ䣬����ϵͳ��Ӧ�ó����ã�ʡȥ�����ĸ�������ʱ��
2.�б���ʹ�ñ�����ʽ������ʹ���¼�֪ͨ��ʽ����һ���׽��ֵ����ݵ��ˣ�����ϵͳ�͹�ȥ�������������ˣ���
"""

def service_client(new_socket, request):
	"""Ϊ����ͻ��˷�������"""
	# 1.������������������󣬼�http����
	# GET / HTTP/1.1
	# ......
	# request = new_socket.recv(1024).decode("utf-8")
	# print(">>>"*50)
	# print(request)
	
	request_lines = request.splitlines()  # �ַ������зָ�󣬷���ֵ��һ���б�
	print("")
	print(">>>"*50)
	print("request_lines = %s" % str(request_lines))  # ��ӡ�б��������б�ת�����ַ�
	
	print("")
	print("-"*20)
    # ��request_lines[0]�� ������ 'GET /index.html HTTP/1.1' ������ƥ�䵽 GET /index.html
    ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
	print(ret)
	file_name = ""
	if ret:
		file_name = ret.group(1)  # ƥ�䵽 /index.html
		#print("file_name = %s" % file_name)
		if file_name == "/":
			file_name = "/index.html"
		

	# 2.����http��ʽ�����ݣ��������
	try:
		f = open("./html"+ file_name, "rb")
	except:
		response = "HTTP/1.1 404 NOT FONUD\r\n"
		response += "\r\n"
		response += "----------file not fonud---------"
		new_socket.send(response.encode("utf-8"))  # �Զ����Ʒ���
		
	else:	
		html_content = f.read()
		f.close()
		response_body = html_content

		# 2.1׼�����͸������������---header
		response_header = "HTTP/1.1 200 OK\r\n"
		response_header += "Content-Length:%d\r\n" % len(response_body)  # ��֪������������ݰ���С���Է�ֹ�����һֱתȦȦ�ȴ���
		response_header += "\r\n"
		print("%s" % response_header)
		# 2.2׼�����͸������������--body
		# response += "hahahaha"
		# new_socket.send(response.encode("utf-8"))
		
		# ��response ���͸������

		response = response_header.encode("utf-8") + response_body  # header �� body ���붼�Ƕ����Ʋ������
		new_socket.send(response)

	# �ر��׽���
	# new_socket.close() 


def main():
	"""�����������Ŀ���"""
	# 1.�����׽���
	tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ���õ��������ȵ���close() ��������4�λ��ֺ���Դ�ܹ������ͷš���ͱ�֤�´����г��򣬿�������������˿ڡ�
	tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
	
	# 2.��
	tcp_server_socket.bind(("", 8080))

	# 3.��Ϊ�����׽���
	tcp_server_socket.listen(128)
	tcp_server_socket.setblocking(False)  # ���׽��ֱ�Ϊ�Ƕ���

	# ����һ��epoll���󼰴��������ڴ�
	epl = select.epoll()
	
	# �������׽��ֶ�Ӧ��fdע�ᵽepoll�У���⵽����������
	epl.register(tcp_server_socket.fileno(), select.EPOLLIN)

	fd_event_dict = dict()  # ����client_socket ����׽��ִ�ʱ�����ڣ���˲����ֵ䷽ʽ��¼��ͬ�ͻ��˵��׽���

	while True:
    """
    1. tcp_server_socket.fileno() = new_socket �����¿ͻ����룬�Ż�������ֵ����һ�ε��ú󣬻��ٴδ��ڶ���״̬��Ҳ���Ǽ���״̬��
    2. fd_event_dict[fd] = client_socket: ���Ѵ��ڿͻ��˼����Ӧ��socket��Ϣ
    3. epl.poll()���¼��б�
    """
		
		fd_event_list = epl.poll()  # Ĭ�ϻ������ֱ�� os��⵽���ݵ��� ͨ���¼�֪ͨ��ʽ ����������򣬴�ʱ�Ż�����
		print ("%s" % str(epl.poll()))
		# [(fd, event), (�׽��ֶ�Ӧ���ļ��������� ����ļ�������������ʲô�¼� ���� ���Ե���recv���յ�)]
		for fd, event in fd_event_list:
        """
        �յ��¼�֪ͨ�������������
        1. �µĿͻ����ӣ�tcp_server_socket.fileno()�����һ��ֵ��ͨ���ж�ʱ���б����fd �Ƿ�������ֵ���ж��Ƿ����µĿͻ�����
        2. �����ӿͻ�������Ϣ��ͨ���ж���������¿ͻ����ӣ��Ǿ������пͻ���������Ϣ
        """
			if fd == tcp_server_socket.fileno():
                # �ж��Ƿ����¿ͻ�����
				new_socket, client_addr = tcp_server_socket.accept()
				epl.register(new_socket.fileno(), select.EPOLLIN)
				fd_event_dict[new_socket.fileno()] = new_socket
			elif event == select.EPOLLIN:
				# �ж��Ѿ����ӵĿͻ����Ƿ������ݷ��͹���
				recv_data = fd_event_dict[fd].recv(1024).decode("utf-8")
				if recv_data:
					service_client(fd_event_dict[fd], recv_data)
				else:
					fd_event_dict[fd].close()
					eql.unregister(fd)  # ɾ�������ڴ����յ���Ӧnull���׽���
					del fd_event_dict[fd]  # ɾ���ֵ��� ��Ӧ���յ�null ���׽���
					
		# 5.Ϊ����ͻ��ķ���
		#p = threading.Thread(target=service_client, args=(new_socket, ))
		#p.start()
		# service_client(new_socket)
		#new_socket.close()
	        #gevent.spawn(service_client, new_socket)

	# 6.�رռ����׽���
	tcp_server_socket.close()


if __name__ == "__main__":
	main()
