import pygame as pg
import random
import time
import math


pg.init()

screen_width = 800
screen_height = 1000

white = (255, 255, 255)
black = (0, 0, 0)

screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("上に向かうゲーム")

#追加部分：diff
# 弾が出現する前の遅延を追跡する変数
initial_bullet_delay = 0
running = True
clock = pg.time.Clock()
delay_timer = initial_bullet_delay  # 遅延タイマーを初期化

#プレイヤーのサイズと初期位置、移動速度を設定
player_width = 50
player_height = 50
player_x = (screen_width - player_width) // 2
player_y = screen_height - player_height - 30
player_speed = 10
speed_multiplier = 1

#プレイヤーの進んだ距離を記録する変数
r = 0
goal = 10000

#弾の最大数やサイズ、速度、生成間隔を設定
## 何も難易度が選択されなかったらmediumにする
max_bullets = 15
bullet_width = 15
bullet_height = 15
bullet_speed = 5

homing_bullet_turn = 0



            
#追加部分：diff
# ゲームの難易度設定
# create_bullet()の一度に生成する弾の数 もいじっていいかも
global difficulty
maina_speed = 0.2

# difficulty = "easy"
if difficulty == "easy":
    max_bullets = 10
    bullet_width = 10
    bullet_height = 10
    bullet_speed = 3
    maina_speed = 0.3

elif difficulty == "medium":
    max_bullets = 15
    bullet_width = 15
    bullet_height = 15
    bullet_speed = 5
    maina_speed = 0.2


elif difficulty == "hard":
    max_bullets = 20
    bullet_width = 20
    bullet_height = 20
    bullet_speed = 7
    maina_speed = 0.1


else:
    print("無効な難易度が選択されました。デフォルトの難易度に設定します。")

print(difficulty)

enemy_img_lst = ["ProjExD_05/uni.png", "ProjExD_05/gomi.png", "ProjExD_05/bin.png"]
enemy_img = enemy_img_lst[random.randint(0, len(enemy_img_lst)-1)]
enemy_img = pg.image.load(enemy_img)
enemy_img = pg.transform.scale(enemy_img, (bullet_width, bullet_height))

min_bullet_interval = 10  # 最小の弾の出現間隔
max_bullet_interval = 30  # 最大の弾の出現間隔
bullet_interval = 0  # 初期の出現間隔
bullet_timer = 0  # タイマー
bullets = []

# 追加部分: ポイントの初期化とポイントに関する変数
points = 0
point_font = pg.font.Font(None, 36)

# 追加部分: 1秒ごとにポイントを増やすための変数
point_increase_timer = 0
points_per_second = 10  # 1秒ごとに増えるポイント数

# 追加部分: 赤くなる状態の関連変数
red_duration = 0
red_effect_frames = 200
red = False

blue_duration = 0
blue_effect_frames = 500
blue = False

# プレイキャラクター画像を取得
explosion_ef = pg.image.load("ProjExD_05/explosion.gif")
chara = pg.image.load("ProjExD_05/3.png")

# 背景画像の読み込み
bg_img = pg.image.load("ProjExD_05/fig/kumo38.png")
rotated_bg_img = pg.transform.flip(bg_img, False, True)

# 闇の画像をロード
dark_size = 1.5
d_img = pg.image.load("ProjExD_05/darkness.jpeg")
d_img = pg.transform.rotozoom(d_img, 0, dark_size)
d_img_top = pg.transform.flip(d_img, False, True)

#一定の間隔で複数の弾を生成。ランダムな位置から弾を生成し、リストbulletsに追加
def create_bullet():
    global bullet_timer, bullet_interval
    bullet_timer += 1
    if bullet_timer > bullet_interval:
        num_bullets = random.randint(1, 2)  # 一度に生成する弾の数
        for _ in range(num_bullets):
            bullet_x = random.randint(0, screen_width - bullet_width)
            bullet_y = 0
             #追加部分：diff
            if random.random() < 0.10:  # 10%の確率で"homing"ラベルを持つ弾を生成
                homing_bullet_speed = bullet_speed/1.1  # ホーミング弾の速度係数
                mai_speed = 10
                bullets.append([bullet_x, bullet_y, "homing",homing_bullet_speed,mai_speed,0])
            else:
                bullets.append([bullet_x, bullet_y, "normal",0,0])
           #bullets.append([bullet_x, bullet_y])
        bullet_interval = random.randint(min_bullet_interval, max_bullet_interval)
        bullet_timer = 0

#プレイヤーと弾の衝突を判定
def is_collision(player_x, player_y, bullet_x, bullet_y):
    if (not red and
            player_x < bullet_x + bullet_width and
            player_x + player_width > bullet_x and
            player_y < bullet_y + bullet_height and
            player_y + player_height > bullet_y):
        return True
    return False

running = True
clock = pg.time.Clock()
dark_y = screen_height # 闇の初期位置
dark_speed = 1 # 闇の浸食する速さ
# scroll_area = 2/5 # スクロールを開始する範囲（一番上から）

# 画像をスクロールさせる為に必要な変数ども
bg_height = 1080
tmr = 0
bg_y = 0
bg_y_2 = bg_height
scroll_area = 1/2 # スクロールを開始する範囲（一番上から）

move_key_dic = {
                pg.K_UP: (0, -5),
                pg.K_DOWN: (0, +5),
                pg.K_LEFT: (-5, 0),
                pg.K_RIGHT: (+5, 0),
}

### キャラクターの方向を管理する関数
def player_direction(player_img):
    """
    引数1 player_img: 画像データ
    """
    # player_img = pg.image.load(f"{img_path}")
    player_img = pg.transform.rotozoom(player_img, 0, 2.0)
    player_trans_img = pg.transform.flip(player_img, True, False)
    
    return {
        (0, 0): player_img, # 初期位置（左)
        (+5, 0): player_trans_img,  # 右
        (+5, -5): pg.transform.rotozoom(player_trans_img, 45, 1.0),  # 右上
        (0, -5): pg.transform.rotozoom(player_img, -90, 1.0),  # 上 # 最初はplayer_trans_img, 90
        (-5, -5): pg.transform.rotozoom(player_img, -45, 1.0),  # 左上
        (-5, 0): player_img,  # 左
        (-5, +5): pg.transform.rotozoom(player_img, 45, 1.0),  # 左下
        (0, +5): pg.transform.rotozoom(player_trans_img, -90, 1.0),  # 下
        (+5, +5): pg.transform.rotozoom(player_trans_img, -45, 1.0),  # 右下
    }


#プレイヤーのキー入力
#弾の生成、移動、描画、画面外に出た弾は削除
#プレイヤーと弾の衝突を検出、衝突した場合はゲームを終了。

### """プレイキャラクター初期設定"""
# global playable_path # 値はtitle.pyで更新される
global chara_idx # 値はtitle.pyで更新される
# chara_idx=0
playable_lst = ["ProjExD_05/3.png", "ProjExD_05/koba.png", "ProjExD_05/bluebird_enjou.png"]
player_img = pg.image.load(playable_lst[chara_idx])
player_img = pg.transform.scale(player_img, (48, 48)) # 48*48にリサイズ
player_direction_dic = player_direction(player_img) # プレイヤーの顔の向きを決める辞書。引数には画像パスを指定
player_img = player_direction_dic[(0, 0)] # 辞書のバリューにある初期の画像を受け取る
player_rect = player_img.get_rect()
player_rect.topleft = (0, 0)
player_speed = 5 # 移動速度
player_x = 365 # 初期x座標
player_y = 890 # 初期y座標
sum_move = [0, 0]


tmr1 = 0
font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30) # 創英角ポップ体サイコー！！

#壁との衝突確認用の関数だ
def check_wall(obj: pg.Rect):
    lst = [0 for i in range(4)]
    for i in range(len(lst)):
        if i == 0:
            if (obj.right>player_x>obj.right-12) and ((player_y+player_height>obj.top) and (player_y<obj.bottom)):
                lst[i] = 1
            else:
                lst[i] = 0
        elif i == 1:
            if (obj.left<player_x+player_width<obj.left+12) and ((player_y+player_height>obj.top) and (player_y<obj.bottom)):
                lst[i] = 1
            else:
                lst[i] = 0
        elif i == 2:
            if (obj.bottom>player_y>obj.bottom-12) and ((player_x+player_width>obj.left) and (player_x<obj.right)):
                lst[i] = 1
            else:
                lst[i] = 0
        elif i == 3:
            if (obj.top<player_y+player_height<obj.top+12) and ((player_x+player_width>obj.left) and (player_x<obj.right)):
                lst[i] = 1
            else:
                lst[i] = 0
            return lst

#障害物(壁)のクラス
class Wall:
    """
    障害物に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    def __init__(self):
        """
        引数に基づき壁Surfaceを作成する
        引数1 color: 壁の色
        """
        color = random.choice(__class__.colors)
        self.img = pg.Surface((280,90))
        self.img.fill(color)
        x = random.randint(0, screen_width-280)
        y = random.randint(0, (screen_height-90)//5)
        pg.draw.rect(self.img, color, (x,y,x+280,y+90))
        self.img.set_colorkey((0, 0, 0))
        self.rect = self.img.get_rect()
        self.rect.center = x+140, y+45

    def update(self, screen:pg.Surface):
        """
        引数 screen 画面Surface
        """
        screen.blit(self.img, self.rect)

wall_num = 2
lst_wall = [0 for i in range(wall_num)]
walls = [Wall() for i in range(wall_num)]

while running:
    # exps = Explosion()
    # 弾が現れるまでの猶予
    if delay_timer > 0:
        delay_timer -= 1
    else:


        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

           
        #現在の距離がゴール以下だとスコアが増加する
        if r <= goal:
            # 追加部分: 1秒ごとにポイントを増やす
            point_increase_timer += 1
            if point_increase_timer == 60:  # 60フレーム = 1秒
                points += points_per_second
                point_increase_timer = 0


    keys = pg.key.get_pressed()
    if r <= goal:
        if keys[pg.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pg.K_RIGHT] and player_x < screen_width - player_width:
            player_x += player_speed
        if keys[pg.K_UP] and player_y > 0:
            player_y -= player_speed
        if keys[pg.K_DOWN] and player_y < screen_height - player_height:
            player_y += player_speed

    # 追加部分: スペースキーでポイントを消費して赤くなる
    if keys[pg.K_SPACE] and points >= 20:
        points -= 20
        red = True
        red_duration = red_effect_frames

    if red:
        red_duration -= 1
        if red_duration <= 0:
            red = False

    
    # 追加部分: Shiftキーでポイントを消費して一定時間操作キャラの速度をあげる
    if keys[pg.K_LSHIFT] and points >= 5:
        points -= 5
        blue = True
        blue_duration = blue_effect_frames
        player_speed *=1.3


    if blue:
        blue_duration -= 1
        if blue_duration <= 0:
            player_speed = 10
            blue = False
            
    # 背景が下端に到達したら反対側にやる
    if bg_y >= bg_height:
        bg_y = -bg_height
    if bg_y_2 >= bg_height:
        bg_y_2 = -bg_height


    # 背景の表示
    screen.blit(bg_img, [0, bg_y])
    screen.blit(rotated_bg_img, [0, bg_y_2])
    
    # 闇を表示
    screen.blit(d_img_top, [0, dark_y])
    screen.blit(d_img, [0, dark_y + (340 * dark_size)])
    if r <= goal:
        dark_y -= dark_speed

    #時間の表示
    txt = font.render(f"Time:{int(tmr1/60):03}", True, (0, 0, 255))
    screen.blit(txt, [600, 10])
    
    # 背景の座標を更新
    tmr += 1
            

    # keys = pg.key.get_pressed()

    for i, wall in enumerate(walls):
        lst_wall[i] = check_wall(wall.rect)
        wall.update(screen)

    if r<=goal:
        if keys[pg.K_LEFT] and player_x > 0:
            for data in lst_wall:
                if data[0] == 1:
                    player_x += player_speed+0.5
                    break
            else:
                player_x -= player_speed

        if keys[pg.K_RIGHT] and player_x < screen_width - player_width:
            for data in lst_wall:
                if data[1] == 1:
                    player_x-=player_speed+0.5
                    break
            else:
                player_x += player_speed

        if keys[pg.K_UP]:
            for data in lst_wall:
                if data[2] == 1:
                    player_y += player_speed+0.5
                    break
            else:
                # 画面上部4分の1範囲にいるときはスクロールする
                if player_y < (screen_height * scroll_area):
                    bg_y += player_speed
                    bg_y_2 += player_speed
                    dark_y += player_speed
                else:
                    player_y -= player_speed

                # 距離が増える
                r += 20

        if keys[pg.K_DOWN]:
            if player_y < screen_height - player_height:
                for data in lst_wall:
                    if data[3] == 1:
                        player_y -= player_speed+0.5
                        break
                else:
                    player_y += player_speed
                # 距離が減る
                if (player_y < 750):
                    r -= 10        
    
    
        
    # """プレイヤーの移動 sum_moveは辞書のキーであるため、常にmax・min ±5の範囲にある"""
    # 辞書のバリューは±5しかないので、keyErrorが起きないよう演算する処理
    for key, move_tpl in move_key_dic.items():
        if keys[key]:
            sum_move[0] += move_tpl[0]
            sum_move[1] += move_tpl[1]  

    ###"""プレイヤーのはみ出し判定"""
    # 移動範囲の制限を追加（プレイヤーが壁を突き抜けないようにする処理）
    # 以下の5と100はどんなに座標が小さくなってもプレイヤーの座標が5と700になるようにするためのもの
    player_x = max(5, min(player_x, screen_width - 100))
    player_y = max(5, min(player_y, screen_height - 100))

    ###"""プレイヤーの顔の向きを選択"""
    # 移動値±5により、KeyErrorとなるのを防ぐための処理
    # sum_moveを加算することで、顔の向きを更新保持する処理
    # (10, y)のときを想定
    if r <= goal:
        if (sum_move[0] > 5):
            sum_move = [0, 0]
            for key, move_tpl in move_key_dic.items():
                if keys[key]:
                    sum_move[0] += move_tpl[0]
                    sum_move[1] += move_tpl[1] 
        # (-10, y)のときを想定
        if (sum_move[0]  < -5):
            sum_move = [0, 0]
            for key, move_tpl in move_key_dic.items():
                if keys[key]:
                    sum_move[0] += move_tpl[0]
                    sum_move[1] += move_tpl[1] 
        # (x, 10)のときを想定
        if (sum_move[1] > 5):
            sum_move = [0, 0]
            for key, move_tpl in move_key_dic.items():
                if keys[key]:
                    sum_move[0] += move_tpl[0]
                    sum_move[1] += move_tpl[1] 
        # (x, -10)のときを想定
        if (sum_move[1] < -5):
            sum_move = [0, 0]
            for key, move_tpl in move_key_dic.items():
                if keys[key]:
                    sum_move[0] += move_tpl[0]
                    sum_move[1] += move_tpl[1] 
        
        # ±5の方向のタプルの辞書キーに応じて、顔の方向の画像を受け取る
        player_img = player_direction_dic[tuple(sum_move)]

        # プレイヤーの位置を直接設定
        player_rect.topleft = (player_x, player_y)
            
    # 移動後の座標にプレイヤーを表示
    screen.blit(player_img, player_rect)

    # 敵（bullet）の生成
    if r < goal:
        create_bullet()
        homing_bullet_turn += 1  # ホーミング弾のターンを増やす
    # exps = pg.sprite.Group()
    
    # 闇が完全に画面を覆いつくしたらゲームオーバー
    if dark_y < 0:
        running = False
    
    # bullets = 二次元リスト
    # bullet  = 敵のx, y座標 を含むリスト
    for bullet in bullets[:]:
        # 通常の弾
            if bullet[2] == "normal":
                bullet[1] += bullet_speed
            #ホーミング
            elif bullet[2] == "homing":
                # "homing" ラベルが付いた弾はプレイヤーに向かって移動
                # プレイヤーの位置と弾の位置を考慮して、弾をプレイヤーに向かって移動させる
                
                if homing_bullet_turn % 1 == 0:  # nターンに1度の頻度でプレイヤーを追跡する
                    homing_bullet_speed = bullet[3]  # ホーミング弾の速度係数

                    player_center_x = player_x + player_width / 2
                    player_center_y = player_y + player_height / 2

                    bullet_center_x = bullet[0] + bullet_width / 2
                    bullet_center_y = bullet[1] + bullet_height / 2

                    # ランダムな微小な角度を追加
                    angle = math.atan2(player_center_y - bullet_center_y, player_center_x - bullet_center_x)
                    angle += random.uniform(-0.1, 0.1)  # ランダムな微小な変化 (-0.2 ～ 0.2 の範囲)

                    # ランダムな速度変化を追加
                    homing_bullet_speed += random.uniform(-1, 1)  # ランダムな速度変化 (-2 ～ 2 の範囲)
            
                    if  bullet[4] <= 0:  # ホーミング弾の持続時間が終わったら、通常の弾に変更する
                        bullet[2] = "normal"
                        print(bullet[2])
                    else:
                        bullet[4] -= maina_speed  # ホーミング弾の持続時間を減少させる
                        print(bullet[4])
                        # プレイヤーの方向に少しずつ移動
                        angle = math.atan2(player_center_y - bullet_center_y, player_center_x - bullet_center_x)
                        bullet[0] += homing_bullet_speed * math.cos(angle)
                        bullet[1] += homing_bullet_speed * math.sin(angle)
                   

            enemy_rect = enemy_img.get_rect()
            enemy_rect.topleft = (bullet[0], bullet[1])
            screen.blit(enemy_img, enemy_rect)
                
                

            if bullet[1] > screen_height:
                bullets.remove(bullet)
            

            if r >= goal:
                bullets.remove(bullet)
            print(red) 
            #追加部分：diff bullet[2]
            if not red and is_collision(player_x, player_y, bullet[0], bullet[1]):
               
                # 衝突時にプレイヤーが爆発するようにする
                screen.blit(explosion_ef, [player_x, player_y])
                pg.display.update()
                time.sleep(0.5) # 死亡エフェクトを目立たせるため、少しだけ停止

                running = False  # ゲームオーバー
                print("ゲームオーバー01")


    #pg.draw.rect(screen, black, [player_x, player_y, player_width, player_height])
    
    
    text_x, text_y = 0, 10 # テキストを表示する位置（x, y）
    #ゴール時の処理
    if r >= goal:
        r = 30000
        txt2 = font.render("game clear", True, (255, 0, 255))
        screen.blit(txt2, [300, 500])
    #ゴールしていないなら
    else:
        txt3 = font.render(f"ゴールまで{goal-r:03}m", True, (255, 0, 255))
        screen.blit(txt3, [text_x, text_y])

    # 追加部分: ポイント表示
    text_diff_x = 10 # テキストの座標をずらす為の変数
    text_diff_y = 30
    if red:
        text = point_font.render("Points: " + str(points) + " (Red for: " + str(red_duration) + " frames)", True, (255, 0, 0))
        screen.blit(text, (text_x + text_diff_x, text_y + text_diff_y))
    else:
        text = point_font.render("Points: " + str(points), True, black)
        screen.blit(text, (text_x + text_diff_x, text_y + text_diff_y))

    invincible_text = point_font.render("Use_Invincible: -20", True, (255, 0, 0))
    screen.blit(invincible_text, (text_x + text_diff_x, text_y + text_diff_y * 2))

    if blue:
        text = point_font.render("Points: " + str(points) + " (Blue for: " + str(blue_duration) + " frames)", True, (0, 0, 255))
        screen.blit(text, (text_x + text_diff_x, text_y + text_diff_y))
    else:
        text = point_font.render("Points: " + str(points), True, black)
        screen.blit(text, (text_x + text_diff_x, text_y + text_diff_y))

    invincible_text = point_font.render("Use_Acceleration: -5", True, (0, 0, 255))
    screen.blit(invincible_text, (text_x + text_diff_x, text_y + text_diff_y * 3))
    
    # screen.blit(player_img, [player_x, player_y])
    # pg.draw.rect(screen, black, [player_x, player_y, player_width, player_height])
    pg.display.update()

    if r <= goal:
        tmr1 += 1

    clock.tick(60)

pg.quit()
