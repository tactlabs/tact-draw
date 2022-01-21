```
wget https://dl.min.io/server/minio/release/linux-amd64/minio

chmod +x minio

sudo mv ./minio /usr/games/minio

minio --version

mkdir minio

cd minio

MINIO_ROOT_USER=admin MINIO_ROOT_PASSWORD=password minio server ./data{1...5} --console-address :9001

```

- add 'data' folder