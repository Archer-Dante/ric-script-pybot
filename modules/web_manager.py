import os


def progress_bar(blocks_transferred, block_size, total_size):
    if total_size > 0:
        percentage = blocks_transferred * block_size * 100 / total_size
        bar_length = 50
        filled_length = int(percentage * bar_length / 100)
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
        print(f"\rЗагрузка: [{bar}] {percentage:.2f}%", end="\r")
        if percentage >= 100:
            print()
    else:
        print(f"Загружено: {blocks_transferred * block_size} байт", end="\r")
    pass
