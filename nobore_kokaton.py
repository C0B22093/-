import pygame as pg
import random
import time

pg.init()

screen_width = 800
screen_height = 1000

white = (255, 255, 255)
black = (0, 0, 0)

screen = pg.display.set_mode((screen_width, screen_height))
pg.display.set_caption("上に向かうゲーム")

#プレイヤーのサイズと初期位置、移動速度を設定
player_width = 50
player_height = 50
player_x = (screen_width - player_width) // 2
player_y = screen_height - player_height - 30
player_speed = 10

#プレイヤーの進んだ距離を記録する変数
r = 0
goal = 20000

#弾の最大数やサイズ、速度、生成間隔を設定
max_bullets = 10
bullet_width = 10
bullet_height = 10
bullet_speed = 10

min_bullet_interval = 10  # 最小の弾の出現間隔
max_bullet_interval = 30  # 最大の弾の出現間隔
bullet_interval = 0  # 初期の出現間隔
bullet_timer = 0  # タイマー
bullets = []

# プレイキャラクター画像を取得
explosion_ef = pg.image.load("ex05/explosion.gif")
chara = pg.image.load("ex05/3.png")

# 背景画像の読み込み
bg_img = pg.image.load("ex05/fig/kumo38.png")
rotated_bg_img = pg.transform.flip(bg_img, False, True)

# 闇の画像をロード
dark_size = 1.5
d_img = pg.image.load("ex05/darkness.jpeg")
d_img = pg.transform.rotozoom(d_img, 0, dark_size)
d_img_top = pg.transform.flip(d_img, False, True)

#一定の間隔で複数の弾を生成。ランダムな位置から弾を生成し、リストbulletsに追加
def create_bullet():
    global bullet_timer, bullet_interval
    bullet_timer += 1
    if bullet_timer > bullet_interval:
        num_bullets = random.randint(1, 3)  # 一度に生成する弾の数
        for _ in range(num_bullets):
            bullet_x = random.randint(0, screen_width - bullet_width)
            bullet_y = 0
            bullets.append([bullet_x, bullet_y])
        bullet_interval = random.randint(min_bullet_interval, max_bullet_interval)
        bullet_timer = 0

running = True
clock = pg.time.Clock()
dark_y = screen_height # 闇の初期位置
dark_speed = 2 # 闇の浸食する速さ
scroll_area = 2/5 # スクロールを開始する範囲（一番上から）

# 画像をスクロールさせる為に必要な変数ども
bg_height = 1080
tmr = 0
bg_y = 0
bg_y_2 = bg_height
scroll_area = 2/5 # スクロールを開始する範囲（一番上から）

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

# 🚩
### """プレイキャラクター初期設定"""
# global playable_path # 値はtitle.pyで更新される
global chara_idx # 値はtitle.pyで更新される
playable_lst = ["ex05/3.png", "ex05/koba.png", "ex05/bluebird_enjou.png"]
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
# 🚩

tmr1 = 0
font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)

#壁との衝突確認用の関数だ
def check_wall(obj: pg.Rect):
    lst = [0 for i in range(4)]
    for i in range(len(lst)):
        if i == 0:
            if (obj.right>player_x>obj.left) and ((player_y+player_height>obj.top) and (player_y<obj.bottom)):
                lst[i] = 1
            else:
                lst[i] = 0
        elif i == 1:
            if (obj.left<player_x+player_width<obj.right) and ((player_y+player_height>obj.top) and (player_y<obj.bottom)):
                lst[i] = 1
            else:
                lst[i] = 0
        elif i == 2:
            if (obj.bottom>player_y>obj.top) and ((player_x+player_width>obj.left) and (player_x<obj.right)):
                lst[i] = 1
            else:
                lst[i] = 0
        elif i == 3:
            if (obj.top<player_y+player_height<obj.bottom) and ((player_x+player_width>obj.left) and (player_x<obj.right)):
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
        y = random.randint(0, screen_height-90)
        pg.draw.rect(self.img, color, (x,y,x+280,y+90))
        self.img.set_colorkey((0, 0, 0))
        self.rect = self.img.get_rect()
        self.rect.center = x+140, y+45

    def update(self, screen:pg.Surface):
        """
        引数 screen 画面Surface
        """
        screen.blit(self.img, self.rect)

wall_num = 3
lst = [0 for i in range(wall_num)]
walls = [Wall() for i in range(wall_num)]

while running:
    screen.fill(white) # 背景色を設定
    # exps = Explosion()


    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            
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
            

    keys = pg.key.get_pressed()

    for i, wall in enumerate(walls):
        lst[i] = check_wall(wall.rect)
        wall.update(screen)

    if r<=goal:
        if keys[pg.K_LEFT] and player_x > 0:
            for data in lst:
                if data[0] == 1:
                    player_x += player_speed+0.5
                    break
            else:
                player_x -= player_speed

        if keys[pg.K_RIGHT] and player_x < screen_width - player_width:
            for data in lst:
                if data[1] == 1:
                    player_x-=player_speed+0.5
                    break
            else:
                player_x += player_speed

        if keys[pg.K_UP]:
            for data in lst:
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
                for data in lst:
                    if data[3] == 1:
                        player_y -= player_speed+0.5
                        break
                else:
                    player_y += player_speed
                # 距離が減る
                if (player_y < 750):
                    r -= 10        
    
    
        
    # 🚩
    """
    プレイヤーの移動
    sum_moveは辞書のキーであるため、常にmax・min ±5の範囲にある
    """
    # 辞書のバリューは±5しかないので、keyErrorが起きないよう演算する処理
    for key, move_tpl in move_key_dic.items():
        if keys[key]:
            sum_move[0] += move_tpl[0]
            sum_move[1] += move_tpl[1]  

    """
    プレイヤーのはみ出し判定
    """
    # 移動範囲の制限を追加（プレイヤーが壁を突き抜けないようにする処理）
    # 以下の5と100はどんなに座標が小さくなってもプレイヤーの座標が5と700になるようにするためのもの
    player_x = max(5, min(player_x, screen_width - 100))
    player_y = max(5, min(player_y, screen_height - 100))

    """
    プレイヤーの顔の向きを選択
    """
    # 移動値±5により、KeyErrorとなるのを防ぐための処理
    # sum_moveを加算することで、顔の向きを更新保持する処理
    # (10, y)のときを想定
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
    # 🚩

    # 敵（bullet）の生成
    if r < goal:
        create_bullet()
    # exps = pg.sprite.Group()
    
    # 闇が完全に画面を覆いつくしたらゲームオーバー
    if dark_y < 0:
        running = False
    
    # bullets = 二次元リスト
    # bullet  = 敵のx, y座標 を含むリスト
    for bullet in bullets[:]:
        bullet[1] += bullet_speed
        pg.draw.rect(screen, black, [bullet[0], bullet[1], bullet_width, bullet_height])

        if bullet[1] > screen_height:
            bullets.remove(bullet)

        # bulletとプレイヤーの衝突判定
        # if (player_x < bullet[0] < player_x + player_width or
        #     bullet[0] < player_x < bullet[0] + bullet_width) and (
        #     player_y < bullet[1] < player_y + player_height or
        #     bullet[1] < player_y < bullet[1] + bullet_height):

        #     # 衝突時にプレイヤーが爆発するようにする
        #     screen.blit(explosion_ef, [player_x, player_y])
        #     pg.display.update()
        #     time.sleep(0.5) # 死亡エフェクトを目立たせるため、少しだけ停止
        #     running = False  # ゲームオーバー
    
    #ゴール時の処理
    if r >= goal:
        r = 30000
        txt2 = font.render("game clear", True, (255, 0, 255))
        screen.blit(txt2, [300, 500])
    #ゴールしていないなら
    else:
        txt3 = font.render(f"ゴールまで{goal-r:03}m", True, (255, 0, 255))
        screen.blit(txt3, [0, 10])
    
    # screen.blit(player_img, [player_x, player_y])
    # pg.draw.rect(screen, black, [player_x, player_y, player_width, player_height])
    pg.display.update()

    if r <= goal:
        tmr1 += 1

    clock.tick(60)

# pg.quit()
import pygame
import random

pygame.init()

screen_width = 800
screen_height = 1000

white = (255, 255, 255)
black = (0, 0, 0)

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("上に向かうゲーム")

#プレイヤーのサイズと初期位置、移動速度を設定
player_width = 50
player_height = 50
player_x = (screen_width - player_width) // 2
player_y = screen_height - player_height - 30
player_speed = 10
speed_multiplier = 1

#弾の最大数やサイズ、速度、生成間隔を設定
max_bullets = 10
bullet_width = 10
bullet_height = 10
bullet_speed = 10

min_bullet_interval = 10  # 最小の弾の出現間隔
max_bullet_interval = 30  # 最大の弾の出現間隔
bullet_interval = 0  # 初期の出現間隔
bullet_timer = 0  # タイマー
bullets = []

# 追加部分: ポイントの初期化とポイントに関する変数
points = 0
point_font = pygame.font.Font(None, 36)

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




#一定の間隔で複数の弾を生成。ランダムな位置から弾を生成し、リストbulletsに追加
def create_bullet():
    global bullet_timer, bullet_interval
    bullet_timer += 1
    if bullet_timer > bullet_interval:
        num_bullets = random.randint(1, 3)  # 一度に生成する弾の数
        for _ in range(num_bullets):
            bullet_x = random.randint(0, screen_width - bullet_width)
            bullet_y = 0
            bullets.append([bullet_x, bullet_y])
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
clock = pygame.time.Clock()


#プレイヤーのキー入力
#弾の生成、移動、描画、画面外に出た弾は削除
#プレイヤーと弾の衝突を検出、衝突した場合はゲームを終了。

while running:
    screen.fill(white) 

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 追加部分: 1秒ごとにポイントを増やす
    point_increase_timer += 1
    if point_increase_timer == 60:  # 60フレーム = 1秒
        points += points_per_second
        point_increase_timer = 0

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
        player_x += player_speed
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < screen_height - player_height:
        player_y += player_speed

    # 追加部分: スペースキーでポイントを消費して赤くなる
    if keys[pygame.K_SPACE] and points >= 20:
        points -= 20
        red = True
        red_duration = red_effect_frames

    if red:
        red_duration -= 1
        if red_duration <= 0:
            red = False

    
    # 追加部分: Shiftキーでポイントを消費して一定時間操作キャラの速度をあげる
    if keys[pygame.K_LSHIFT] and points >= 5:
        points -= 5
        blue = True
        blue_duration = blue_effect_frames
        player_speed *=2


    if blue:
        blue_duration -= 1
        if blue_duration <= 0:
            player_speed = 10
            blue = False

    #生成
    create_bullet()

    for bullet in bullets[:]:
        bullet[1] += bullet_speed
        pygame.draw.rect(screen, black, [bullet[0], bullet[1], bullet_width, bullet_height])

        if bullet[1] > screen_height:
            bullets.remove(bullet)

        if not red and is_collision(player_x, player_y, bullet[0], bullet[1]):
            running = False  # ゲームオーバー
            print("ゲームオーバー")

    # 追加部分: ポイント表示
    if red:
        text = point_font.render("Points: " + str(points) + " (Red for: " + str(red_duration) + " frames)", True, (255, 0, 0))
        screen.blit(text, (10, 10))
    else:
        text = point_font.render("Points: " + str(points), True, black)
        screen.blit(text, (10, 10))

    invincible_text = point_font.render("Use_Invincible: -20", True, (255, 0, 0))
    screen.blit(invincible_text, (10, 60))

    if blue:
        text = point_font.render("Points: " + str(points) + " (Blue for: " + str(blue_duration) + " frames)", True, (0, 0, 255))
        screen.blit(text, (10, 10))
    else:
        text = point_font.render("Points: " + str(points), True, black)
        screen.blit(text, (10, 10))

    invincible_text = point_font.render("Use_Acceleration: -5", True, (0, 0, 255))
    screen.blit(invincible_text, (10, 90))


    pygame.draw.rect(screen, black, [player_x, player_y, player_width, player_height])
    pygame.display.update()

    clock.tick(60)

pygame.quit()
