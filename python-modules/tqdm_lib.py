from tqdm import tqdm
import random

lisp_array = [i**2 for i in tqdm(range(0, 5000000))]
random.shuffle(lisp_array)
print("Checked the Progeress Bar")