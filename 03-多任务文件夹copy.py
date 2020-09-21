liesun102@liesun102-vm:~/Desktop/python��ҵ��/python-06$ cat 08-����\:�������ļ���copy.py 
import os
import multiprocessing

def copy_file(q,file_name,old_folder_name,new_folder_name):
	"""����ļ��и���"""
	# print("------ģ��copy�ļ�: ��%s----->%s �ļ����ǣ�%s" % (old_folder_name, new_folder_name, file_name))	
	old_f = open(old_folder_name + "/" + file_name, "rb")
	content = old_f.read()
	old_f.close()

	new_f = open(new_folder_name + "/" + file_name, "wb")
	new_f.write(content)
	new_f.close()
	
	# ����������ļ�����ô���������д��һ����Ϣ����ʾ�Ѿ����
	q.put(file_name)


def main():
	# ��ȡ�û�Ҫcopy���ļ�������
	old_folder_name = input("������Ҫcopy���ļ������֣�")
	# ����һ�����ļ���
	try:
		new_folder_name = old_folder_name + "[����]"
		os.mkdir(new_folder_name)	
	except:
		pass
	# ��ȡ�ļ��е����д�copy���ļ��� listdir()
	file_names = os.listdir(old_folder_name)
	print(file_names)
	
	# �������̳�
	po = multiprocessing.Pool(5)

	# ����һ������
	q = multiprocessing.Manager().Queue()

	# �����ļ����е��ļ������µ��ļ�����ȥ
	for file_name in file_names:
		po.apply_async(copy_file, args=(q,file_name,old_folder_name,new_folder_name))

	po.close()
	#po.join()
	all_file_num = len(file_names)
	copy_ok_num = 0
	while True:
		file_name = q.get()
		# print("�����copy��%s" % file_name)	
		copy_ok_num += 1
		print("\r��������Ϊ��%f" % (copy_ok_num/all_file_num),end="")
		if copy_ok_num >= all_file_num:
			break
	print()


if __name__ == "__main__":
main()