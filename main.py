import os
import shutil


def extract(filepath, output_dir, extract_image=False):
    with open(filepath, "rb") as binary_file:
        name, ext = os.path.splitext(os.path.basename(filepath))
        binary_file.seek(0, os.SEEK_END)
        num_bytes = binary_file.tell()

        jpg_found = False
        for i in range(num_bytes):
            binary_file.seek(i)

            if extract_image and not jpg_found:
                jpg_end_bytes = binary_file.read(4)
                if jpg_end_bytes == b"\xFF\xD9\x00\x00":
                    binary_file.seek(0)
                    jpg_data = binary_file.read(i + 4)
                    image_output = os.path.join(output_dir, f"{name}_image.jpg")
                    with open(image_output, "wb") as img_out:
                        img_out.write(jpg_data)
                    jpg_found = True

            else:
                mp4_start_bytes = binary_file.read(16)
                if mp4_start_bytes == b"\x00\x00\x00\x18\x66\x74\x79\x70\x6D\x70\x34\x32\x00\x00\x00\x00":
                    binary_file.seek(i)
                    mp4_data = binary_file.read(num_bytes - i)
                    mp4_output = os.path.join(output_dir, f"{name}.mp4")
                    with open(mp4_output, "wb") as mp4_out:
                        mp4_out.write(mp4_data)
                    return mp4_output  # 返回新视频路径
    return None


def copy_with_timestamp(src, dst):
    shutil.copy2(src, dst)  # 自动保留修改时间


def batch_extract(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        filepath = os.path.join(input_folder, filename)
        if not os.path.isfile(filepath):
            continue

        name, ext = os.path.splitext(filename)
        ext = ext.lower()

        try:
            if ext == ".jpg":
                result = extract(filepath, output_folder)
                if result:  # 是动态图，提取出视频
                    # 同步时间戳
                    mod_time = os.path.getmtime(filepath)
                    os.utime(result, (mod_time, mod_time))
                else:
                    # 静态图像直接复制
                    copy_with_timestamp(filepath, os.path.join(output_folder, filename))
            elif ext in [".png", ".jpeg", ".mp4", ".mov"]:
                copy_with_timestamp(filepath, os.path.join(output_folder, filename))
            else:
                print(f"跳过非媒体文件: {filename}")
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")

if __name__ == "__main__":
    input_dir = "./test"
    output_dir = "./output"
    batch_extract(input_dir, output_dir)
