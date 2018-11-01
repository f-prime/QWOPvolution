from PIL import Image
import pytesseract
from selenium import webdriver
import pykeyboard
import time
import _thread as thread
import random
import re
import time

class GeneticQWOP(object):
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.set_window_size(638, 473)
        self.keyboard = pykeyboard.PyKeyboard()
        self.population = []
        self.alive = True
        self.population_size = 10
        self.mutation_rate = 10
        self.score = 0.0
        self.time_limit = 120 # Seconds

    def generate_dna(self):
        choices = [
            "Q",
            "W",
            "O",
            "P",
            "QW",
            "QO",
            "QP",
            "WO",
            "WP",
            "OP",
            "QWO",
            "WOP",
            "QOP",
            "QWP",
            "QWOP"
        ] 
        self.start_time = time.time()
        dna = []

        for x in range(10):#random.randint(50, 100)):
            dna.append(
                    (random.choice(choices), self.generate_time())
            )
        
        return dna

    def generate_time(self):
        return random.randint(100, 3000) / 1000

    def generate_population(self):
        self.population = []
        for x in range(self.population_size):
            dna = self.generate_dna()
            self.population.append(dna)

    def mate(self, org1, org2):
        visited = {}
        population = []
        for x in range(self.population_size):
            position = random.randint(0, len(org1))
            if not visited.get(position):
                visited[position] = True
                if random.randint(0, 100) > 50:
                    child = org1[0:position] + org2[position:]        
                    if random.randint(0, 100) <= self.mutation_rate:
                        print("MUTATED")
                        index = random.randint(0, len(child) - 1)
                        child[index] = self.generate_dna()[0]
                    population.append(child)
                else:
                    child = org2[0:position] + org1[position:]
                    if random.randint(0, 100) < self.mutation_rate:
                        print("MUTATED")
                        index = random.randint(0, len(child) - 1)
                        child[index] = self.generate_dna()[0]
                    population.append(child)
            else:
                population.append(self.generate_dna())

        print("Offspring: ", population)            
        self.population = population

    def restart_game(self):
        self.keyboard.tap_key(' ')

    def check_done(self):
        self.driver.get_screenshot_as_file('/tmp/qwop.png')
        img = Image.open('/tmp/qwop.png')
        height = img.height
        width = img.width
        middle = int(width / 2)
        start_x = middle - 130
        start_y = 20

        score_offset_x = 100
        score_offset_y = 30
        score = img.crop(
                (start_x,
                start_y,
                start_x + score_offset_x, 
                start_y + score_offset_y)
        )
      
        score.save('/tmp/cropped_qwop.png')

        cd_start_x = middle + 55
        cd_start_y = int(height / 2) + 120

        restart = pytesseract.image_to_string(img)
        is_done = 'everyone is a winner' in restart or 'PARTICI PANT' in restart or 'PARTICIPANT' in restart or 'NATIONAL' in restart or 'HERO' in restart
        score = pytesseract.image_to_string(score)
        score_filtered = re.findall("\-?[0-9]+\.[0-9]+", score)
        if score_filtered:
            self.score = float(score_filtered[0])
        if "NATIONAL" in restart or "HERO" in restart and self.score < 100:
            self.score = 100
        return is_done
        
    def main(self):
        self.open_qwop()
        input("Tap when ready")
        print("Preparing...")
        time.sleep(5)
        self.generate_population()
        best_1 = best_2 = None
        while True:
            print("Mom:", best_1)
            print("Dad:", best_2)
            for org in self.population:
                is_done = self.check_done()
                thread.start_new_thread(self.run, (org,))                 
                self.start_time = time.time()
                while not is_done:
                    print("ELAPSED TIME:", time.time() - self.start_time)
                    if time.time() - self.start_time > self.time_limit:
                        print("TIME IS UP")
                        self.keyboard.tap_key('r')
                        break
                    is_done = self.check_done()
                delta = time.time() - self.start_time                
                if self.score >= 2:
                    speed = self.score / delta
                else:
                    speed = 0
                if speed > 1: # Usually this happens when the time gets messed up
                    speed = 0.03
                    
                print("RUN", self.score, delta, speed)
                print("MOM", best_1)
                print("DAD", best_2)

                if not best_1:
                    best_1 = (org, self.score, delta, speed)
                elif not best_2:
                    best_2 = (org, self.score, delta, speed)
                elif (speed > 0 and best_1[3] < speed) or (speed == 0 and best_1[1] >= self.score and best_1[3] == 0):
                    print("NEW MOM")
                    best_2 = best_1
                    best_1 = (org, self.score, delta, speed)
                elif (speed > 0 and best_2[3] < speed) or (speed == 0 and best_2[1] >= self.score and best_2[3] == 0):
                    print("NEW DAD")
                    best_2 = (org, self.score, delta, speed)
                self.alive = False                
                self.restart_game()
                self.alive = True
                print("Restarting...")
            print("Mating...")
            self.mate(best_1[0], best_2[0])

    def run(self, dna):
        print("New DNA")
        while self.alive:
            for keys in dna:
                if not self.alive:
                    break
                for key in keys[0]:
                    self.keyboard.press_key(key)
                time.sleep(keys[1])
                for key in keys[0]:
                    self.keyboard.release_key(key)

    def open_qwop(self):
        self.driver.get("http://www.foddy.net/Athletics.html")


if __name__ == "__main__":
    GeneticQWOP().main()
