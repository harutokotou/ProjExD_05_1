import math
import random
import sys
import time

import pygame as pg




def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾，こうかとん，ビーム）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or 1600 < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or 900 < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class My_tank(pg.sprite.Sprite):
    """
    ゲームキャラクター（mytank）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        mytank画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()

        img0 = pg.transform.rotozoom(pg.image.load(f"ex05/fig/my_tank.png"), 45, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのmy戦車
        
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


      



    



    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
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
    
    def get_direction(self) -> tuple[int, int]:
        return self.dire

class Screen(pg.sprite.Sprite):

    def __init__(self, width, height, title):
        # width:画面の横サイズ, height:画面の縦のサイズ, title:タイトル
        super().__init__()
        self.width, self.height = width, height
        pg.display.set_caption(title) #タイトルの設定
        self.disp = pg.display.set_mode((self.width, self.height))#画面のサイズ

    def blit(self, *args, **kwargs): #*args は位置引数がタプルに、 **kwargs はキーワード引数が辞書として渡される
        self.disp.blit(*args, **kwargs)
class teki_tank(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    delta2 = {  # 押下キーと移動量の辞書
        pg.K_w: (0, -1),
        pg.K_s: (0, +1),
        pg.K_a: (-1, 0),
        pg.K_d: (+1, 0),
    }
    def __init__(self, num: int, xy: tuple[int, int]):

        super().__init__()
        teki_Img = pg.transform.rotozoom(pg.image.load(f"ex05/fig/my_tank.png"), 45, 2.0)
        teki_Img2 = pg.transform.flip(teki_Img, True, False)  # デフォルトのmy戦車
        
        self.imgs = {
            (+1, 0): teki_Img2,  # 右
            (+1, -1): pg.transform.rotozoom(teki_Img2, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(teki_Img2, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(teki_Img, -45, 1.0),  # 左上
            (-1, 0): teki_Img,  # 左
            (-1, +1): pg.transform.rotozoom(teki_Img, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(teki_Img2, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(teki_Img2, -45, 1.0),  # 右下
        }
        
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10


        self.state = "normal"  # 初期状態は通常状態
        self.hyper_life = -1
    
    def update(self, key_lst: list[bool], screen: pg.Surface):
        key = pg.key.get_pressed()
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        if key_lst[pg.K_LSHIFT]:
            self.speed = 2
        else:
            self.speed = 1

        sum_mv = [0, 0]
        for k, mv in __class__.delta2.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(self.rect) != (True, True):
            for k, mv in __class__.delta2.items():
                if key_lst[k]:
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]

    
    def get_direction(self) -> tuple[int, int]:
        return self.dire

def main():
    #使用するフォント
    screen = Screen(1600, 900, "タンクサバイバー") #ゲームウィンドウの幅 # ゲームウィンドウの高さ
    bg_img = pg.image.load("ex05/fig/pg_bg.jpg") #背景画像を読み込み
    bg2_img = pg.image.load("ex05/fig/pg_bg2.jpg") 

    font_score, font_time = pg.font.Font(None, 150), pg.font.Font(None, 200)

  
    text1, text2 = pg.font.Font(None, 250), pg.font.Font(None, 150)  #二つのフォントとサイズを読み込む
    screen_num = 0      #スタート画面、プレイ画面、結果画面切り替え用numの初期化

    #タイマー
    time = 60            #時間の初期化
    pg.time.set_timer(pg.USEREVENT, 1000)       #1秒ごとにUSEREVENTを実行
    text = font_time.render(f"{str(int(time))}s", True, (255, 255, 255))      #描画する経過時間の設定

   



    tanks = pg.sprite.Group() #戦車用のコンテナの作成
    tanks.add(My_tank(3, (200, 700)),teki_tank(3, (1400, 200)))


    while True:
        key_lst = pg.key.get_pressed()

        if screen_num == 0:
            pg.display.update()
            screen.disp.blit(bg2_img, [0, 0])
            font_text1 = text1.render("TANK SURVIVOR", True, (0,0,0)) #テキストの設定　(文字、滑らか、色)
            font_text2 = text2.render("---->> Start Push Space <<----", True, (0,0,0))
            screen.disp.blit(font_text1,[100, 350]) #テキストを描画
            screen.disp.blit(font_text2,[80, 700])

            if key_lst[pg.K_SPACE]:         #spaceキーが押されたとき       
                screen_num =1           #screan_numを1にして場面転換
                
        if screen_num == 1:
            pg.display.update()
            screen.disp.blit(bg_img, [0, 0])
            tanks.update(key_lst, screen)
            tanks.draw(screen)

            text = font_time.render(f"{str(int(time))}s", True, (255, 255, 255))      #描画する経過時間の設定
            screen.disp.blit(text, [700, 20])

        if screen_num == 2:
            screen.disp.fill((0,0,0))
            pg.display.update()

        
            

        for event in pg.event.get(): 
                if event.type == pg.QUIT: #QUITになったらFalse
                    return 0
                if event.type == pg.USEREVENT: #タイマーイベント発生
                    time -= 10
                    if time < 0:
                        screen_num = 2
                    

                    
                    
                


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()