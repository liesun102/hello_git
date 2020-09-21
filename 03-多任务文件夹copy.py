liesun102@liesun102-vm:~/Desktop/python就业班/python-06$ cat 08-案例\:多任务文件夹copy.py 
import os
import multiprocessing

def copy_file(q,file_name,old_folder_name,new_folder_name):
	"""完成文件夹复制"""
	# print("------模拟copy文件: 从%s----->%s 文件名是：%s" % (old_folder_name, new_folder_name, file_name))	
	old_f = open(old_folder_name + "/" + file_name, "rb")
	content = old_f.read()
	old_f.close()

	new_f = open(new_folder_name + "/" + file_name, "wb")
	new_f.write(content)
	new_f.close()
	
	# 如果拷贝完文件，那么就向队列中写入一个消息，表示已经完成
	q.put(file_name)


def main():
	# 获取用户要copy的文件夹名字
	old_folder_name = input("请输入要copy的文件夹名字：")
	# 创建一个新文件夹
	try:
		new_folder_name = old_folder_name + "[复件]"
		os.mkdir(new_folder_name)	
	except:
		pass
	# 获取文件夹的所有待copy的文件名 listdir()
	file_names = os.listdir(old_folder_name)
	print(file_names)
	
	# 创建进程池
	po = multiprocessing.Pool(5)

	# 创建一个队列
	q = multiprocessing.Manager().Queue()

	# 复制文件夹中的文件，到新的文件夹中去
	for file_name in file_names:
		po.apply_async(copy_file, args=(q,file_name,old_folder_name,new_folder_name))

	po.close()
	#po.join()
	all_file_num = len(file_names)
	copy_ok_num = 0
	while True:
		file_name = q.get()
		# print("已完成copy：%s" % file_name)	
		copy_ok_num += 1
		print("\r拷贝进度为：%f" % (copy_ok_num/all_file_num),end="")
		if copy_ok_num >= all_file_num:
			break
	print()


if __name__ == "__main__":
main()