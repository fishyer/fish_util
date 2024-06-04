import yaml

class ConfigManager:
    @staticmethod
    def read_yaml(file_path):
        with open(file_path, 'r') as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    @staticmethod
    def write_yaml(data, file_path):
        with open(file_path, 'w') as outfile:
            try:
                yaml.safe_dump(data, outfile, default_flow_style=False)
            except yaml.YAMLError as exc:
                print(exc)



def main():
    print(f"[run main: {__file__}]")
    # 读取 YAML 文件
    config = ConfigManager.read_yaml('alog/config/config.yaml')
    print(config)

    # 写入 YAML 文件
    data = {
        'name': 'John Doe',
        'job': 'Developer',
        'skills': ['Python', 'Java', 'C++'],
    }
    ConfigManager.write_yaml(data, 'alog/config/config.yaml')

if __name__ == "__main__":
    main()