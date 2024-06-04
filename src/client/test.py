def get_active_tasks_size(tasks_data):
    """
    获取active_tasks中每个任务列表的大小

    :param tasks_data: 包含active_tasks信息的字典
    :return: 一个字典，其键为active_tasks中的任务名称，值为该任务下列表的长度
    """
    sizes = {}
    active_tasks = tasks_data.get("active_tasks", {})

    for task_name, task_list in active_tasks.items():
        sizes[task_name] = len(task_list)

    return sizes


# 示例数据
tasks_data = {
    "active_tasks": {"celery@yutianran.lan": [], "celery@another.example": [1, 2, 3]},
}

# 调用函数并打印结果
sizes = get_active_tasks_size(tasks_data)
print(sizes)
