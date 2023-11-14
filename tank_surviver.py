import math
import random
import sys
import time
import os
import pygame as pg




def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾,my戦車、敵戦車）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or 1600 < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or 900 < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate

class Screen(pg.sprite.Sprite):

    def __init__(self, width, height, title):
        # width:画面の横サイズ, height:画面の縦のサイズ, title:タイトル
        super().__init__()
        self.width, self.height = width, height
        pg.display.set_caption(title) #タイトルの設定
        self.disp = pg.display.set_mode((self.width, self.height))#画面のサイズ

    def blit(self, *args, **kwargs): #*args は位置引数がタプルに、 **kwargs はキーワード引数が辞書として渡される
        self.disp.blit(*args, **kwargs)
class My_Tank(pg.sprite.Sprite):
    """
    ゲームキャラクター（mytank）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }
    
    

    def __init__(self, xy: tuple[int, int],max_shots: int = 20,initial_stock: int = 3):
        """
        mytank画像Surfaceを生成する
        引数1 xy:Mytank画像の位置座標タプル
        引数2 max_shots 発射回数
        """
        super().__init__()
        

        Mytank_img = pg.transform.rotozoom(pg.image.load(f"fig/my_tank.png"), 45, 2.0)
        Mytank_img2 = pg.transform.flip(Mytank_img, True, False)  # デフォルトのmy戦車
                
        self.imgs = {
            (+1, 0): Mytank_img2,  # 右
            (0, -1): pg.transform.rotozoom(Mytank_img2, 90, 1.0),  # 上
            (-1, 0): Mytank_img,  # 左
            (0, +1): pg.transform.rotozoom(Mytank_img, 90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(Mytank_img2, -45, 1.0),  # 右下
            (+1, -1): pg.transform.rotozoom(Mytank_img2, 45, 1.0),  # 右上
            (-1, -1): pg.transform.rotozoom(Mytank_img, -45, 1.0),  # 左上
            (-1, +1): pg.transform.rotozoom(Mytank_img, 45, 1.0),  # 左下
        }

        self.dire = (+1, 0) #初期状態を右向きに設定
        self.image = self.imgs[self.dire]#方向に応じた画像を保管
        self.rect = self.image.get_rect()#rectは短形領域を表す
        self.rect.center = xy#rectの中心を指定された位置座標xyにセンタリング
        self.speed = 1 #スピードを1に設定

        self.remaining_shots = max_shots  # 初期の残り発射回数
        self.last_shot_time = pg.time.get_ticks()  # 最後に Bomb を発射した時間

        self.stock = initial_stock  # 初期のストック
        
        

    
    def update(self, key_lst: list[bool], screen: pg.Surface,walls:pg.sprite.Group, my_bombs: pg.sprite.Group):
        """
        押下キーに応じてteki_tankを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        押下されたキーに対応する移動量を delta 辞書を参照して取得し
        それに従ってタンクを移動させます。
        """
        sum_mv = [0, 0]#sum_mvを初期化
        for k, mv in __class__.delta.items():#各キーとタプルを二つのリストに分ける
            if key_lst[k]:#もし指定されたキーが押された場合、sum_mvに加算して移動方向を計算
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        if check_bound(self.rect) != (True, True):#画面外判定
            for k, mv in __class__.delta.items():#もう一度キーと対応する移動ベクトルをループする
                if key_lst[k]:#もう一度キーと対応する移動ベクトルをループする
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])

        if not (sum_mv[0] == 0 and sum_mv[1] == 0):#タンクが移動している場合、移動ベクトルを新しい方向として設定
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]

        # #壁と爆弾の衝突
        # for bomb in my_bombs:
        #     bomb.update(walls)

        # 壁と戦車の衝突時に反射
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if sum_mv[0] != 0:
                    self.rect.move_ip(-self.speed * sum_mv[0], 0)
                if sum_mv[1] != 0:
                    self.rect.move_ip(0, -self.speed * sum_mv[1])
        
    def get_direction(self) -> tuple[int, int]:#方向のタプルを取得する
        return self.dire

    def shoot_bomb(self, my_bombs: pg.sprite.Group):
        """
        引数1 bombs:Bomb グループ
        戦車から爆弾を発射します。
        """
        if self.remaining_shots > 0:
            new_bomb = My_Bomb(self)
            my_bombs.add(new_bomb)
            self.remaining_shots -= 1
  

    def draw_remaining_shots(self, screen, font):
        """
        画面に残りの爆弾ショットを描画します。
        """
        remaining_shots_text = font.render(f"shots: {self.remaining_shots}| Stock: {self.stock}", True, (255, 255, 255))
        screen.blit(remaining_shots_text, [10, 10])

    def respawn(self):
        """
        戦車を初期位置に再スポーンさせる
        """
        self.rect.center = (200, 700)  # 初期位置にセンタリング
    

    


class Teki_tank(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    delta2 = {  # 押下キーと移動量の辞書
        pg.K_w: (0, -1),
        pg.K_s: (0, +1),
        pg.K_a: (-1, 0),
        pg.K_d: (+1, 0),
    }
    def __init__(self,xy: tuple[int, int],max_shots: int = 20,initial_stock: int = 3):

        super().__init__()
        teki_img = pg.transform.rotozoom(pg.image.load(f"fig/my_tank.png"), 45, 2.0)
        teki_img2 = pg.transform.flip(teki_img, True, False)  # デフォルトのmy戦車
        
        self.imgs = {
            (+1, 0): teki_img2,  # 右
            (0, -1): pg.transform.rotozoom(teki_img2, 90, 1.0),  # 上
            (-1, 0): teki_img,  # 左
            (0, +1): pg.transform.rotozoom(teki_img2, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(teki_img2, -45, 1.0),  # 右下
            (+1, -1): pg.transform.rotozoom(teki_img2, 45, 1.0),  # 右上
            (-1, -1): pg.transform.rotozoom(teki_img, -45, 1.0),  # 左上
            (-1, +1): pg.transform.rotozoom(teki_img, 45, 1.0),  # 左下
        }
        
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 1

        self.remaining_shots = max_shots  # 初期の残り発射回数
        self.last_shot_time = pg.time.get_ticks()  # 最後に Bomb を発射した時間

        self.stock2 = initial_stock  # 初期のストック

    
    def update(self, key_lst: list[bool], screen: pg.Surface, walls: pg.Surface, teki_bombs: pg.sprite.Group):
        key = pg.key.get_pressed()
        """
        押下キーに応じてteki_tankを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        押下されたキーに対応する移動量を delta 辞書を参照して取得し
        それに従ってタンクを移動させます。
        """
        sum_mv = [0, 0]#sum_mvを初期化
        for k, mv in __class__.delta2.items():#各キーとタプルを二つのリストに分ける
            if key_lst[k]:#もし指定されたキーが押された場合、sum_mvに加算して移動方向を計算
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]

        if check_bound(self.rect) != (True, True):#画面外判定
            for k, mv in __class__.delta2.items():#もう一度キーと対応する移動ベクトルをループする
                if key_lst[k]:#もう一度キーと対応する移動ベクトルをループする
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])

        if not (sum_mv[0] == 0 and sum_mv[1] == 0):#タンクが移動している場合、移動ベクトルを新しい方向として設定
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        
        #   # 壁と爆弾の衝突
        # for bomb in teki_bombs:
        #     bomb.update(walls)


        # 壁と戦車の衝突時に反射
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if sum_mv[0] != 0:
                    self.rect.move_ip(-self.speed * sum_mv[0], 0)
                if sum_mv[1] != 0:
                    self.rect.move_ip(0, -self.speed * sum_mv[1])

    
    def get_direction(self) -> tuple[int, int]:#方向のタプルを取得する
        return self.dire
    
    def shoot_bomb(self, teki_bombs: pg.sprite.Group):
        """
        引数1 bombs:Bomb グループ
        戦車から爆弾を発射します。
        """
        if self.remaining_shots > 0:
            new_bomb = My_Bomb(self)
            teki_bombs.add(new_bomb)
            self.remaining_shots -= 1
  

    def draw_remaining_shots(self, screen, font):
        """
        画面に残りの爆弾ショットを描画します。
        """
        remaining_shots_text = font.render(f"shots: {self.remaining_shots}| Stock: {self.stock2}", True, (255, 255, 255))
        screen.blit(remaining_shots_text, [1250,10])

    def respawn(self):
        """
        戦車を初期位置に再スポーンさせる
        """
        self.rect.center = (1400,200)  # 初期位置にセンタリング

class My_Bomb(pg.sprite.Sprite):
    """
    自陣の戦車の爆弾クラス
    """
    def __init__(self, my_tank: My_Tank):
        """
        爆弾画像Surfaceを生成する
        """
        super().__init__()
        self.vx, self.vy = my_tank.get_direction()
        self.image = pg.transform.rotozoom(pg.image.load("fig/bakudan_2.GIF"), 90, 1.0)
        self.rect = self.image.get_rect(center=my_tank.rect.center)
        self.speed = 3
        self.reflect_count = 0  # 反射回数
        

    def update(self,walls: pg.sprite.Group,tank2: pg.sprite.Group):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 
        壁や戦車との衝突を処理します。
        """
       
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)

        # 壁との衝突
        if pg.sprite.spritecollideany(self, walls):
            # 爆弾が壁に当たった場合の処理
            self.vx = -self.vx  # x方向の反射
            self.vy = -self.vy  # y方向の反射
            self.rect.move_ip(self.speed * self.vx, self.speed * self.vy)
        
        # 進行方向からの角度を変更して反射
        # if self.vx != 0 and self.vy != 0:
        #     angle = math.atan2(self.vy, self.vx)  # 現在の進行方向の角度を計算
        #     # 90度回転
        #     angle += math.radians(90)
        #     # 新しい進行方向を計算
        #     self.vx = math.cos(angle)
        #     self.vy = math.sin(angle)
        #         # 移動
        #     self.rect.move_ip(self.speed * self.vx, self.speed * self.vy)
        # スクリーンとの衝突
        if self.rect.left < 0 or self.rect.right > 1600:
            self.vx *= -1
            self.reflect_count += 1

        if self.rect.top < 0 or self.rect.bottom > 900:
            self.vy *= -1
            self.reflect_count += 1

        # 三回反射したら Bomb を削除
        if self.reflect_count >= 2:
            self.kill()
        

        # # tank1 との衝突を確認
        # tank1_hit = pg.sprite.spritecollide(self, tank1, False)
        # if tank1_hit:
        #     self.kill()  # 爆弾を削除
        # tank2 との衝突を確認
        tank2_hit = pg.sprite.spritecollide(self, tank2, False)
        if tank2_hit:
            self.kill()  # 爆弾を削除

        
        



        # 爆弾が画面外に出たか確認
        if not check_bound(self.rect):
            self.kill()  # 爆弾を削除
 
        #壁にぶつかったら削除if check_bound(self.rect) != (True, True):
            #self.kill()
class Teki_Bomb(pg.sprite.Sprite):
    """
    自陣の戦車の爆弾クラス
    """
    def __init__(self, teki_tank: Teki_tank):
        """
        爆弾画像Surfaceを生成する
        """
        super().__init__()
        self.vx, self.vy = teki_tank.get_direction()
        self.image = pg.transform.rotozoom(pg.image.load("fig/bakudan_2.GIF"), 90, 1.0)
        self.rect = self.image.get_rect(center=teki_tank.rect.center)
        self.speed = 3
        self.reflect_count = 0  # 反射回数
        

    def update(self,walls: pg.sprite.Group,tank1: pg.sprite.Group):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 
        壁や戦車との衝突を処理します。
        """
       
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)

        # 壁との衝突
        if pg.sprite.spritecollideany(self, walls):
            # 爆弾が壁に当たった場合の処理
            self.vx = -self.vx  # x方向の反射
            self.vy = -self.vy  # y方向の反射
            self.rect.move_ip(self.speed * self.vx, self.speed * self.vy)
        
        # 進行方向からの角度を変更して反射
        # if self.vx != 0 and self.vy != 0:
        #     angle = math.atan2(self.vy, self.vx)  # 現在の進行方向の角度を計算
        #     # 90度回転
        #     angle += math.radians(90)
        #     # 新しい進行方向を計算
        #     self.vx = math.cos(angle)
        #     self.vy = math.sin(angle)
        #         # 移動
        #     self.rect.move_ip(self.speed * self.vx, self.speed * self.vy)
        # スクリーンとの衝突
        if self.rect.left < 0 or self.rect.right > 1600:
            self.vx *= -1
            self.reflect_count += 1

        if self.rect.top < 0 or self.rect.bottom > 900:
            self.vy *= -1
            self.reflect_count += 1

        # 三回反射したら Bomb を削除
        if self.reflect_count >= 2:
            self.kill()
        

        # tank1 との衝突を確認
        tank1_hit = pg.sprite.spritecollide(self, tank1, False)
        if tank1_hit:
            self.kill()  # 爆弾を削除
        
        # # tank2 との衝突を確認
        # tank2_hit = pg.sprite.spritecollide(self, tank2, False)
        # if tank2_hit:
        #     self.kill()  # 爆弾を削除

        # 爆弾が画面外に出たか確認
        if not check_bound(self.rect):
            self.kill()  # 爆弾を削除
 
        #壁にぶつかったら削除if check_bound(self.rect) != (True, True):
            #self.kill()
class Wall(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj, life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()

        img = pg.image.load("fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()

def main():
    #使用するフォント
    screen = Screen(1600, 900, "タンクサバイバー") #ゲームウィンドウの幅 # ゲームウィンドウの高さ
    font_score, font_time = pg.font.Font(None, 150), pg.font.Font(None, 200)
    text1, text2 = pg.font.Font(None, 250), pg.font.Font(None, 150)  #フォントとサイズを読み込む
    text3 = pg.font.Font(None,250)
    Bom_count = pg.font.Font(None, 50)
    Bom_count2 = pg.font.Font(None,50)
    #サウンド
    sounds = [pg.mixer.Sound("sound/bakudan.mp3"),pg.mixer.Sound("sound/start.wav"), \
                pg.mixer.Sound("sound/boom.wav"),pg.mixer.Sound("sound/ou.mp3"),\
                    pg.mixer.Sound("sound/win.mp3"),pg.mixer.Sound("sound/hikiwake.mp3")]
    
    #背景画像を読み込み
    bg_img = pg.image.load("fig/pg_bg.jpg") # (ゲーム内)
    bg2_img = pg.image.load("fig/pg_bg2.jpg") #(初期状態)
    bg3_img = pg.image.load("fig/pg_bg3.jpg") #(引き分け)

    
    #タイマー
    time = 60    #時間の初期化
    pg.time.set_timer(pg.USEREVENT, 1000) #1秒ごとにUSEREVENTを実行

    #壁の設定
    tate_bar1 = Wall(775, 300, 30, 300, (102, 102, 102))
    yoko_bar1 = Wall(300, 300, 475, 30, (102, 102, 102))
    yoko_bar2 = Wall(775, 600, 475, 30, (102, 102, 102))

    screen_num = 0   #スタート画面、プレイ画面、結果画面切り替え用numの初期化

    #戦車用のコンテナの作成
    tank1 = pg.sprite.Group() 
    tank2 = pg.sprite.Group()
    #戦車用のインスタンス追加
    tank1.add(My_Tank((200,700)))
    tank2.add(Teki_tank((1400,200)))

    # 爆弾用のコンテナ作成
    teki_bombs = pg.sprite.Group()
    my_bombs = pg.sprite.Group()


    # 壁用のコンテナ作成
    walls = pg.sprite.Group(tate_bar1, yoko_bar1, yoko_bar2)

    #爆発用のコンテナ作成
    teki_exps = pg.sprite.Group()
    my_exps = pg.sprite.Group()
        

    while True:
        key_lst = pg.key.get_pressed()  #押されたキーを取得
        if screen_num == 0: #スタート画面
            screen.disp.blit(bg2_img, [0, 0])
            font_text1 = text1.render("TANK SURVIVOR", True, (0,0,0)) #テキストの設定　(文字、滑らか、色)
            font_text2 = text2.render("---->> Start Push Space <<----", True, (0,0,0))
            screen.disp.blit(font_text1,[100, 350]) #テキストを描画
            screen.disp.blit(font_text2,[80, 700])
            pg.display.update()


            for event in pg.event.get():
                if event.type == pg.QUIT: return

                if key_lst[pg.K_SPACE]:     #spaceキーが押されたとき 
                    sounds[1].play()    
                    screen_num =1           #screen_numを1にして場面転換
                
            
                
        if screen_num == 1: #ゲーム画面
            screen.disp.blit(bg_img, [0, 0])

            #bombsの残り弾数カウント
            for tank_bom in tank1:
                tank_bom.draw_remaining_shots(screen, Bom_count)

            for tank_bom2 in tank2:
                tank_bom2.draw_remaining_shots(screen, Bom_count2)

            #タイマー表示
            text = font_time.render(f"{str(int(time))}s", True, (255, 255, 255))
            screen.disp.blit(text, [700, 20])

            # 爆弾と戦車の衝突を確認

            for tank in tank1:
            # tank1の爆弾との衝突判定
                teki_bombs_hit_tank = pg.sprite.spritecollide(tank, teki_bombs, True)
                for bomb in teki_bombs_hit_tank:
                    my_exps.add(Explosion(teki_bombs, 100))  # 敵の爆発エフェクトを生成（必要に応じてlifeを調整）
                    sounds[2].play()
                    tank.stock -= 1  # ストックを減らす
                    if tank.stock <= 0:  # ストックがなくなったら
                        tank.kill()  # 戦車を消す
                        sounds[4].play()
                        screen_num = 2
                    else:
                        tank.respawn()  # 戦車を初期位置に再スポーン


            for teki_tank in tank2:
                # tank2の爆弾との衝突判定
                my_bombs_hit_teki_tank = pg.sprite.spritecollide(teki_tank, my_bombs, True)
                for bomb in my_bombs_hit_teki_tank:
                    teki_exps.add(Explosion(teki_tank, 200))  # 敵の爆発エフェクトを生成（必要に応じてlifeを調整）
                    sounds[2].play()
                    teki_tank.stock2 -= 1  # ストックを減らす
                    if teki_tank.stock2 <= 0:  # ストックがなくなったら
                        teki_tank.kill()  # 戦車を消す
                        sounds[4].play()
                        screen_num = 2
                    else:
                        teki_tank.respawn()  # 戦車を初期位置に再スポーン

            # 味方の爆弾との衝突判定をスキップ
            my_bombs_hit_teki_tank = pg.sprite.spritecollide(teki_tank, my_bombs, True)
            for bomb in my_bombs_hit_teki_tank:
                # ここに味方の爆発エフェクト生成および音の再生を追加
                pass  # 何もしない




            # for tank in tank1:
            #     bombs_hit_tank = pg.sprite.spritecollide(tank, bombs, True)
            #     for bomb in bombs_hit_tank:
            #         exps.add(Explosion(tank, 100))  # 爆発エフェクトを生成（必要に応じてlifeを調整）
            #         sounds[2].play()
            #         tank.stock -= 1  # ストックを減らす
            #         if tank.stock <= 0:  # ストックがなくなったら
            #             tank.kill()  # 戦車を消す
            #             sounds[4].play()
            #             screen_num = 2
            #         else:
            #             tank.respawn()  # 戦車を初期位置に再スポーン


            # for teki_tank in tank2:
            #     bombs_hit_teki_tank = pg.sprite.spritecollide(teki_tank, bombs, True)
            #     for bomb in bombs_hit_teki_tank:
            #         exps.add(Explosion(teki_tank, 200))  # 爆発エフェクトを生成（必要に応じてlifeを調整）
            #         sounds[2].play()
            #         teki_tank.stock2 -= 1  # ストックを減らす
            #         if teki_tank.stock2 <= 0:  # ストックがなくなったら
            #             teki_tank.kill()  # 戦車を消す
            #             sounds[4].play()
            #             screen_num = 2
            #         else:
            #             teki_tank.respawn()  # 戦車を初期位置に再スポーン
                    

            
            tank1.update(key_lst, screen, walls, my_bombs)
            tank1.draw(screen)
            tank2.update(key_lst, screen, walls,teki_bombs)
            tank2.draw(screen)
            my_bombs.update(walls,tank2)
            my_bombs.draw(screen)
            teki_bombs.update(walls,tank1)
            teki_bombs.draw(screen)
            walls.draw(screen)
            teki_exps.update()
            teki_exps.draw(screen)
            my_exps.update()
            my_exps.draw(screen)
            

            pg.display.update()

            for event in pg.event.get():
                if event.type == pg.QUIT: #QUITになったらFalse
                    return 0
                if event.type == pg.KEYDOWN and event.key == pg.K_RSHIFT:
                    sounds[0].play()
                    tank1.sprites()[0].shoot_bomb(my_bombs)# tanksグループからshoot_bombメソッド呼び出し
            
                if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
                    sounds[0].play()
                    tank2.sprites()[0].shoot_bomb(teki_bombs)# tanksグループからshoot_bombメソッド呼び出し
              
                if event.type == pg.USEREVENT: #タイマーイベント発生
                    time -= 1
                    if time < 0:
                       sounds[5].play()
                       screen_num = 2

        if screen_num == 2:#引き分け画面
            pg.display.update()
            screen.disp.blit(bg3_img, [0, 0])
            

            #得点の表示
            if tank.stock > teki_tank.stock2:#my_tank勝利
                screen.disp.blit(text1.render("My_tank win!!!", True, (0, 0, 0)), [100, 450])
                txt = f"My:{tank.stock}  Teki:{teki_tank.stock2}"
                screen.disp.blit(text1.render(txt, True, (0,0,0)), [100, 100])
                font_text2 = text2.render("---->> Go Back Push Space <<----", True, (0,0,0))
                screen.disp.blit(font_text2,[80, 700])
            elif tank.stock < teki_tank.stock2:#teki_tank勝利
                screen.disp.blit(text1.render("Teki_tank win!!!", True, (0,0,0)), [100, 450])
                txt = f"My:{tank.stock}  Teki:{teki_tank.stock2}"
                screen.disp.blit(text1.render(txt, True, (0,0,0)), [100, 100])
                font_text2 = text2.render("---->> Go Back Push Space <<----", True, (0,0,0))
                screen.disp.blit(font_text2,[80, 700])
            else:
                screen.disp.blit(text3.render("Drow !!",True,(0,0,0)),[600,450])
                txt = f"My:{tank.stock}  Teki:{teki_tank.stock2}"
                screen.disp.blit(text1.render(txt, True, (0,0,0)), [100, 100])
                font_text2 = text2.render("---->> Go Back Push Space <<----", True, (0,0,0))
                screen.disp.blit(font_text2,[80, 700])
                                

            for event in pg.event.get():
                if event.type == pg.QUIT: return

                if key_lst[pg.K_SPACE]:     #spaceキーが押されたとき、新たに初期化処理を行う。
                    sounds[3].play() 
                    tank1 = pg.sprite.Group()
                    tank2 = pg.sprite.Group()
                    bombs = pg.sprite.Group()
                    walls = pg.sprite.Group(Wall(775, 300, 30, 300, (102, 102, 102)),
                                            Wall(300, 300, 475, 30, (102, 102, 102)),
                                            Wall(775, 600, 475, 30, (102, 102, 102)))
                    exps = pg.sprite.Group()
                    time = 60
                    tank1.add(My_Tank((200,700)))
                    tank2.add(Teki_tank((1400,200)))
                    screen_num = 0         
            
   
        

        
                    

    


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()