import math
import random
import sys
import time

import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ


def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾，戦車，ビーム）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：戦車SurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（戦車）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        戦車画像Surfaceを生成する
        引数1 num：戦車画像ファイル名の番号
        引数2 xy：戦車画像の位置座標タプル
        """
        super().__init__()

        img0 = pg.transform.rotozoom(pg.image.load(f"fig/my_tank.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトの戦車
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }

        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10


        self.state = "normal"  # 初期状態は通常状態
        self.hyper_life = -1


    def change_img(self, num: int, screen: pg.Surface):
        """
        戦車画像を切り替え，画面に転送する
        引数1 num：戦車画像ファイル名の番号
        引数2 screen：画面Surface
        """

        self.image = pg.transform.rotozoom(pg.image.load(f"ex04/fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)


    
    def change_state(self,state,hyper_life):
        """
        戦車の状態を切り替えるメゾット
        引数1 state: 状態を表す
        引数2 hyper_life: 発動時間
        """
        self.state = state
        self.hyper_life = hyper_life



    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じて戦車を移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """


        if key_lst[pg.K_LSHIFT]:
            self.speed = 2
        else:
            self.speed = 1

        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(self.rect) != (True, True):
            for k, mv in __class__.delta.items():
                if key_lst[k]:
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]


        if self.state == "hyper":
            self.hyper_life -= 1
            self.image = pg.transform.laplacian(self.image)
            if self.hyper_life < 0:
                self.change_state("normal", -1)


        screen.blit(self.image, self.rect)
    
    def get_direction(self) -> tuple[int, int]:
        return self.dire


class my_bomb(pg.sprite.Sprite):
    """
    自陣の戦車の爆弾クラス
    """
    def __init__(self, bird: Bird):
        """
        爆弾画像Surfaceを生成する
        """

def main():
    pg.display.set_caption("タンクサバイバー")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")


    bird = Bird(3, (900, 400))
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0

        screen.blit(bg_img, [0, 0])


        bird.update(key_lst, screen)
        pg.display.update()


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()