print("hello world")
import pygame as pg
import random

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



move_key_dic = {
                pg.K_UP: (0, -5),
                pg.K_DOWN: (0, +5),
                pg.K_LEFT: (-5, 0),
                pg.K_RIGHT: (+5, 0),
}

### キャラクターの方向を管理する関数
def player_direction(img_path: str):
    player_img = pg.image.load(f"{img_path}")
    player_img = pg.transform.rotozoom(player_img, 0, 2.0)
    player_trans_img = pg.transform.flip(player_img, True, False)
    
    return {
        (0, 0): player_img, # 初期位置（左)
        (+5, 0): player_trans_img,  # 右
        (+5, -5): pg.transform.rotozoom(player_trans_img, 45, 1.0),  # 右上
        (0, -5): pg.transform.rotozoom(player_trans_img, 90, 1.0),  # 上
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
"""
プレイキャラクター初期設定
"""
player_direction_dic = player_direction("ex05/3.png") # プレイヤーの顔の向きを決める辞書。引数には画像パスを指定
player_img = player_direction_dic[(0, 0)] # 辞書のバリューにある初期の画像を受け取る
player_rect = player_img.get_rect()
player_rect.topleft = (0, 0)
player_speed = 5 # 移動速度
player_x = 365 # 初期x座標
player_y = 890 # 初期y座標
sum_move = [0, 0]
# 🚩

while running:
    screen.fill(white) 

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            

    keys = pg.key.get_pressed()
    if keys[pg.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pg.K_RIGHT] and player_x < screen_width - player_width:
        player_x += player_speed
    if keys[pg.K_UP] and player_y > 0:
        player_y -= player_speed
    if keys[pg.K_DOWN] and player_y < screen_height - player_height:
        player_y += player_speed
    
    
        
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


    """
    プレイヤーの位置を直接設定（当たり判定？）
    """
    # sum_moveはあくまでもキャラクターの描画なので、指定して合わせてあげないとズレが生じる
    # 48はこうかとんの画像サイズ分の当たり判定がなされるようにするためのもの。でもなんかあまり当たり判定変わっていないような気もする
    player_rect.center = (player_x+48, player_y+48)
        
    # 移動後の座標にプレイヤーを表示
    screen.blit(player_img, player_rect)
    # 🚩

    #生成
    create_bullet()

    for bullet in bullets[:]:
        bullet[1] += bullet_speed
        pg.draw.rect(screen, black, [bullet[0], bullet[1], bullet_width, bullet_height])

        if bullet[1] > screen_height:
            bullets.remove(bullet)

        if (player_x < bullet[0] < player_x + player_width or
            bullet[0] < player_x < bullet[0] + bullet_width) and (
            player_y < bullet[1] < player_y + player_height or
            bullet[1] < player_y < bullet[1] + bullet_height):

            running = False  # ゲームオーバー
    

    # screen.blit(player_img, [player_x, player_y])
    # pg.draw.rect(screen, black, [player_x, player_y, player_width, player_height])
    pg.display.update()

    clock.tick(60)

pg.quit()