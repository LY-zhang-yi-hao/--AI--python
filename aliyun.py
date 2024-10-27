from http import HTTPStatus
import dashscope
from dashscope import Generation
import random
import json


class DashScopeAPI:
	def __init__(self):
		# 配置API-KEY
		dashscope.api_key = ""
	
	# 单轮对话
	def call_with_messages(self, messages):
		response = Generation.call(
			model="qwen-turbo",
			messages=messages,
			# 设置随机数种子seed，如果没有设置，则随机数种子默认为1234
			seed=random.randint(1, 10000),
			# 将输出设置为"message"格式
			result_format='message'
		)
		if response.status_code == HTTPStatus.OK:
			print(response.output.choices[0]['message']['content'])
			# print(response)
		else:
			print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
				response.request_id, response.status_code,
				response.code, response.message
			))
	
	# # 多轮对话
	# def multi_round(self, messages):
	# 	response = Generation.call(
	# 		model="qwen-turbo",
	# 		messages=messages,
	# 		result_format='message'  # 将输出设置为"message"格式
	# 	)
	# 	if response.status_code == HTTPStatus.OK:
	# 		# 将assistant的回复添加到messages列表中
	# 		messages.append(
	# 			{'role': response.output.choices[0]['message']['role'],
	# 			 'content': response.output.choices[0]['message']['content']
	# 			 }
	# 		)
	# 	else:
	# 		print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
	# 			response.request_id, response.status_code,
	# 			response.code, response.message
	# 		))
	# 		# 如果响应失败，将最后一条user message从messages列表里删除，确保user/assistant消息交替出现
	# 		messages = messages[:-1]
	# 	# print(messages)
	# 	return messages
	
	# # 流式输出
	# def call_with_stream(self, messages):
	# 	responses = Generation.call(
	# 		model="qwen-turbo",
	# 		messages=messages,
	# 		result_format='message',  # 设置输出为'message'格式
	# 		stream=True,  # 设置输出方式为流式输出
	# 		incremental_output=True  # 增量式流式输出
	# 	)
	# 	for response in responses:
	# 		if response.status_code == HTTPStatus.OK:
	# 			print(response.output.choices[0]['message']['content'], end='')
			
	# 		# 将assistant的回复添加到messages列表中
	# 		# messages.append({'role': response.output.choices[0]['message']['role'],
	# 		#                  'content': response.output.choices[0]['message']['content']})
	# 		# yield json.dumps({'content': response.output.choices[0]['message']['content']}) + '\n'
	# 		else:
	# 			print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
	# 				response.request_id, response.status_code,
	# 				response.code, response.message
	# 			))
	# 			# 如果响应失败，将最后一条user message从messages列表里删除，确保user/assistant消息交替出现
	# 			messages = messages[:-1]


if __name__ == '__main__':
	dsapi = DashScopeAPI()
	messages = [
		{'role': 'system', 'content': 'You are a helpful assistant.'},
		{'role': 'user', 'content': '我的题目，请你，只需要回答答案即可。91、实验室电器设备所引起的火灾，应：A．用水灭火B．用二氧化碳或干粉灭火器灭火C．用泡沫灭火器灭火'},
	]
	# 单轮对话





	dsapi.call_with_messages(messages)
	# 多轮对话
	# dsapi.multi_round(messages)
	# 流式输出
	# dsapi.call_with_stream(messages)