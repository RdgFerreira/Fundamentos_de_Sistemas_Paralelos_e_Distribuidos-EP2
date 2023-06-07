stubs:
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. directory.proto
	python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. integration.proto

run_cli_dir:
	python3 client.py $(arg)

run_serv_dir:
	python3 server.py $(arg)

run_cli_int:
	python3 client_int.py $(arg)

run_serv_int:
	python3 server_int.py $(arg)

clean:
	rm -f directory_pb2.py
	rm -f directory_pb2_grpc.py
	rm -f integration_pb2.py
	rm -f integration_pb2_grpc.py
