import logging
from os import path
from os import walk


if __name__ == '__main__':
    steel_dir = path.join(path.dirname(path.realpath(__file__)), 'steel')
    print(steel_dir)
    data_files = []
    seen_data_files = set()
    data_files = []
    for _, _, files in walk(steel_dir):
        for data_file in files:
            _, ext = path.splitext(data_file)
            if (data_file.startswith('bench_4') or data_file.startswith('bench_2')) and ext.strip().lstrip('.') in {'', 'txt'}:
                data_files.append(path.join(steel_dir, data_file))
    data_files = list(sorted(data_files))

    logging.basicConfig(level=logging.INFO)

    for df in data_files:
        num_capacities = 0
        num_colors = 0
        num_orders = 0
        slab_capacity = []
        order_size = []
        order_color = []
        with open(df, 'r') as steel:
            data = steel.readline().strip().split()
            data = [int(d) for d in data if len(d) > 0]
            num_capacities = data[0]
            slab_capacity = data[1:]
            num_colors = int(steel.readline())
            num_orders = int(steel.readline())
            for _ in range(num_orders):
                line = steel.readline().strip().split()
                line = [int(v) for v in line]
                assert len(line) == 2
                order_size.append(line[0])
                order_color.append(line[1])
        df_path, ext = path.splitext(df)
        dzn_path = df_path + '.dzn'
        logging.info(dzn_path)
        with open(dzn_path, 'w+') as dzn_f:
            dzn_f.writelines([f"Orders = 1..{num_orders};\n",
                              f"Colors = 1..{num_colors};\n",
                              f"Capacities = 1..{num_capacities};\n",
                              "maxColors = 2;\n",
                              f"capacity = {slab_capacity};\n",
                              f"size = {order_size};\n",
                              f"color = {order_color};"])
