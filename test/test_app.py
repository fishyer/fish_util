import fish_script.client.wucai_client as wucai_client
import fish_script.client.eagle_client as eagle_client
import os


def test_add_tjd():
    # 专辑 https://www.sqmuying.com/a/?id=72179
    # 图片 https://tjqew5fe8ew.lt508.com/5eb7a_kmt72179-fc2ce-01.jpg
    # https://tjqew5fe8ew.lt508.com/5eb7a_kmt72179-fc2ce-04.jpg
    # https://tjqew5fe8ew.lt508.com/5eb7a_kmt72179-fc2ce-082.jpg
    # https://tjqew5fe8ew.lt508.com/1zfca_okc52288-01.jpg
    zj_id = 65763
    zj_count = 83
    # https://tjqew5fe8ew.lt508.com/4rgaz_sla65763-01.jpg
    zj_folder_id = eagle_client.get_folder(str(zj_id))["id"]
    print(f"zj_folder_id: {zj_folder_id}")
    zj_url = f"https://www.sqmuying.com/a/?id={zj_id}"
    for i in range(1, zj_count + 1):
        image_url = f"https://tjqew5fe8ew.lt508.com/4rgaz_sla{zj_id}-0{i}.jpg"
        print(image_url)
        image_item = eagle_client.add_item(
            image_url, zj_url, zj_folder_id, f"{zj_id}-{i}"
        )


def main():
    print(__file__)
    test_add_tjd()
    # os.system(f"pytest -qs {__file__}")


if __name__ == "__main__":
    main()
