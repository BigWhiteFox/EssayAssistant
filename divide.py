from pdf2image import convert_from_path
import os


def segmentation(pdf_path):
    # 获得文件的保存路径和文件名(含后缀)
    save_path = pdf_path.name
    file_name = os.path.basename(pdf_path.name)
    # 指定父目录
    output_path = "./pdf_divide"
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # 将PDF转换为图像列表
    images = convert_from_path(save_path)
    # 创建以PDF文件名命名的文件夹在输出文件夹中
    pdf_name = os.path.splitext(os.path.basename(save_path))[0]
    output_path = os.path.join(output_path, pdf_name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # 保存每一页图像到输出文件夹，并按顺序编号
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_path, f'{i + 1}.JPEG')
        image.save(image_path, 'JPEG')
        image_paths.append(image_path)
    return image_paths


