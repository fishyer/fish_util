import pandas as pd
import pymysql
from fish_util.src.log_util import print
import time

customer_set = set()


def execute_sql(cursor, sql, params=None, debug=False):
    try:
        if debug:
            if params:
                print("Executing SQL:", cursor.mogrify(sql, params))
            else:
                print("Executing SQL:", sql)

        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(e)
        return None


# 删除重复记录，根据mobile列的值，保留id最小的记录，其余的删除
def remove_duplicate_records(cursor, table_name, unique_column, debug=False):
    try:
        # 创建临时表存储需要保留的最小 id
        create_temp_table_sql = (
            "CREATE TEMPORARY TABLE temp_table SELECT MIN(id) AS min_id FROM "
            + table_name
            + " GROUP BY "
            + unique_column
        )
        cursor.execute(create_temp_table_sql)

        # 删除除了最小 id 以外的所有记录
        delete_sql = (
            "DELETE FROM "
            + table_name
            + " WHERE id NOT IN (SELECT min_id FROM temp_table)"
        )
        if debug:
            print("Executing SQL:", delete_sql)
        cursor.execute(delete_sql)

        # 删除临时表
        drop_temp_table_sql = "DROP TEMPORARY TABLE temp_table"
        cursor.execute(drop_temp_table_sql)

        return True
    except Exception as e:
        print(e)
        return False


def read_xlsx_data():
    # 从本地读取xlsx文件数据
    xls_path = "/Users/yutianran/Documents/MyCode/crm-pengqi/mysql/crm2-0528.xlsx"
    all_data = pd.read_excel(xls_path)
    print(f"读取数据成功，共{len(all_data)}条数据")
    # data = all_data.iloc[10000:-10]
    # return data
    return all_data


# 查看表结构
def show_columns(cursor):
    sql = "SHOW COLUMNS FROM crm_customer"
    cursor.execute(sql)
    result = cursor.fetchall()
    print("crm_customer表的表结构: ")
    for row in result:
        print(row)


# 批量添加客户数据
def add_customer(cursor, data, debug_mode=False):
    # 打印总行数
    print(len(data))
    # 打印首尾数据
    print(data.head(1))
    print(data.tail(1))
    success_count = 0
    failed_count = 0
    skip_count = 0

    # 批量添加数据到crm_customer表
    count = 0
    for index, row in data.iterrows():
        count += 1
        mobile = row["手机号码"]
        if mobile is None or mobile == "" or mobile == "NaN" or mobile == "nan":
            print(f"count: {count}, 第{index + 2}条数据手机号码为空 skip {row}")
            skip_count += 1
            continue
        mobile = str(mobile)
        name = row["姓名"]
        if (
            pd.isna(name)
            or name is None
            or name == ""
            or name == "NaN"
            or name == "nan"
        ):
            # 则设置row["姓名"]为:客户123****1234,用手机号来拼接
            name = f"客户{str(mobile)[:3]}****{str(mobile)[-4:]}"
        remarks = row["备注"]
        if (
            pd.isna(remarks)
            or remarks is None
            or remarks == ""
            or remarks == "NaN"
            or remarks == "nan"
        ):
            remarks = ""
        params = (name, mobile, remarks)
        print(f"params: {params}")
        # 用一个set来防止重复添加
        if row["手机号码"] in customer_set:
            print(f"count: {count}, 第{index + 2}条数据已存在 skip {params}")
            skip_count += 1
            continue
        sql = "INSERT INTO crm_customer (name, mobile, remarks) VALUES (%s, %s, %s)"
        result = execute_sql(cursor, sql, params, debug=debug_mode)
        if result is None:
            print(f"count: {count}, 第{index + 2}条数据添加失败 failed {params}")
            failed_count += 1
        else:
            print(f"count: {count}, 第{index + 2}条数据添加成功 success {params}")
            success_count += 1
            customer_set.add(row["手机号码"])
        check_count = success_count + failed_count + skip_count
        print(
            f"done{len(data)}条数据,success:{success_count},failed:{failed_count},skip:{skip_count},check:{check_count}"
        )


def main_flow():
    # 统计耗时
    start_time = time.time()
    print("start main function ...")
    data = read_xlsx_data()[2:]
    connection = pymysql.connect(
        # host="127.0.0.1",
        # host="60.205.5.11",
        host="182.92.232.210",
        port=13306,
        user="root",
        password="root",
        database="crm",
    )
    try:
        with connection.cursor() as cursor:
            print("准备执行sql语句")
            show_columns(cursor)
            # remove_duplicate_records2(cursor, "crm_customer", "mobile", debug=True)
            add_customer(cursor, data, False)
        # 提交更改
        connection.commit()
        print("提交更改")
    finally:
        # 关闭数据库连接
        connection.close()
        print("数据库连接已关闭")

    print("end main function ...")
    end_time = time.time()
    all_time = int(end_time - start_time)
    print(f"耗时：{all_time} s, {all_time/60} min")


if __name__ == "__main__":
    main_flow()
