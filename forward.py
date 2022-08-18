'''
活动线报人形 Bot 监控插件（一键命令版）
Author: SuperManito
Version: 1.2
Modified: 2022-06-26

如果阁下喜欢用记事本编辑此脚本，那么如果报错了请不要在群里问，容易挨打

工作原理: 
监控本群线报Bot发送的消息，将二次处理后的命令发送至用户容器Bot通过/cmd命令运行，群线报已新增支持去重功能，默认10分钟内不会重复

配置方法:
自行使用带有语法检测的专业代码编辑器进行配置，首先需要定义你的容器 Bot id (user_id)，监控脚本自行定义，默认附带了几个，注意看注释内容

安装方法:
插件依赖于旧版 PagerMaid (https://gitlab.com/Xtao-Labs/pagermaid-modify) 人形Bot，自行安装，并且需要在部署服务端安装redis数据库( -sh apt-get update ; apt-get install redis -y )，全部配置好后将你的脚本发送到收藏夹，回复 -apt install 进行安装，后期用户更新配置后安装新脚本才能生效

使用方法:
启用监控 -forward enable
关闭监控 -forward disable

友情提示:
给自己的人形部署在网络条件较好的环境里，断网就监控不到了哦，如果bot id配置正确那么每次操作插件都会向你的bot发送一条状态消息

DC1用户慎用！DC5用户放心用。

'''

from telethon.errors.rpcerrorlist import FloodWaitError
from pagermaid import redis, log, redis_status, version ,bot
from pagermaid.utils import lang, alias_command, client
from pagermaid.listener import listener
import re, os

## 定义你的容器 Bot ID
ID_BOT = 1234567890

## 处理命令
async def filters(text):

    ## 定义你的运行账号
    # 凌晨线报较多，合理安排运行账号
    NowHour = os.popen("echo -n $(TZ=UTC-8 date +%H)").read()
    if (NowHour == '00') or (NowHour == '23'):
        LZKJ_RUN_ACCOUNTS = " -c 1,2"
        CJHY_RUN_ACCOUNTS = " -c 1,2"
    elif (NowHour == '01'):
        LZKJ_RUN_ACCOUNTS = " -c 1-4"
        CJHY_RUN_ACCOUNTS = " -c 1-4"
    else:
        LZKJ_RUN_ACCOUNTS = " -c 1-6"
        CJHY_RUN_ACCOUNTS = " -c 1-6"


    # 用户需知:
    # 1. return False 为不执行任何命令
    # 2. 注意代码格式与缩进，建议使用带有语法检测的代码编辑器
    # 3. 超级无线的活动脚本运行账号不要太多，否则ip会黑的很快，目前没有队列功能
    # 4. 你需要了解各个脚本所对应的活动玩法以及活动域名，不要盲目设置监控，不建议监控任何开卡

    ## 常规脚本匹配
    if "task env edit " in text:
        ## 脚本名
        script = re.search(r'/KingRan_KR/(.*?)\b ', text, re.M | re.I)[1]

        # 注释：
        # text += xxx   可以理解为追加 xxx 内容
        # text = text   执行原命令



        # 超级无线 · 关注店铺有礼
        if script == 'jd_wxShopFollowActivity.js':
            text += LZKJ_RUN_ACCOUNTS

        # 超级无线 · 读秒拼手速
        elif script == 'jd_wxSecond.js':
            text += LZKJ_RUN_ACCOUNTS

        # 超级无线 · 通用游戏
        elif script == 'jd_game.js':
            text += LZKJ_RUN_ACCOUNTS
            
        # 加购有礼
        elif script == 'jd_lzaddCart.js':
            text += CJHY_RUN_ACCOUNTS
            
        # lz组队瓜分
        elif script == 'jd_zdjr.js':
            text = text
            
        # 锦鲤
        elif script == 'jd_wxCartKoi.js':
            text += LZKJ_RUN_ACCOUNTS
            
        # 集卡抽奖
        elif script == 'jd_wxCollectCard.js':
            text += LZKJ_RUN_ACCOUNTS
            
        # LZ粉丝
        elif script == 'jd_wxFansInterActionActivity.js':
            text += LZKJ_RUN_ACCOUNTS
            
        # LZ刮刮乐抽奖
        elif script == 'jd_drawCenter.js':
            text += LZKJ_RUN_ACCOUNTS
            
        # CJ组队瓜分
        elif script == 'jd_cjzdgf.js':
            text = text
            
        # 微定制瓜分京豆
        elif script == 'jd_wdz.js':
            text = text
            
        # PKC关注有礼
        elif script == 'jd_txgzyl.js':
            text += LZKJ_RUN_ACCOUNTS
            
        # luck关注有礼
        elif script == 'jd_luck_draw.js':
            text += LZKJ_RUN_ACCOUNTS
            
        # 分享有礼
        elif script == 'jd_share.js':
            text = text

        else:
            return False


    else:
        return False

    text = "/cmd " + text
    return text












## ⚠⚠⚠
## ⬇️ 不懂勿动 ⬇️

## 监控群组ID
ID_FROM = -1001615491008
## 监控消息发送者（由用户id组成的数组）
ID_ARRAY = ["5116402142"]

@listener(is_plugin=False, outgoing=True, command=alias_command('forward'),
          description='\n本插件需要 Redis 数据库环境支持',
          parameters="`线报监控（群用户版）"
                     "\n\n开启监控:\n`-forward enable`"
                     "\n\n关闭监控:\n`-forward disable")
async def shift_set(context):
    error_msg = "出错了呜呜呜 ~ 无法识别的来源对话"
    if not redis_status():
        await context.edit(f"{lang('error_prefix')}{lang('redis_dis')}")
        return
    if context.parameter[0] == "enable":
        redis_name = "bot"
        # 检查来源频道/群组
        try:
            channel = await context.client.get_entity(int(ID_FROM))
            resource_name = channel.title
            channel = int(f'-100{channel.id}')
        except Exception:
            try:
                channel = await context.client.get_entity("bot")
                if not channel.broadcast:
                    await context.edit(error_msg + "2")
                    return
                channel = int(f'-100{channel.id}')
            except Exception:
                await context.edit(error_msg + "3")
                return
        to = int(ID_BOT)
        redis.set(f"{redis_name}." + str(channel), f"{to}")
        await context.edit(f"✅ 已启用针对 {resource_name} 的消息监控")
        await bot.send_message(to, "✅ 已开启线报监控")
        await log(f"监控已启用")
    elif context.parameter[0] == "disable":
        redis_name = "bot"
        # 检查来源频道/群组
        try:
            channel = int(ID_FROM)
        except Exception:
            try:
                channel = (await context.client.get_entity("bot")).id
                if channel.broadcast or channel.gigagroup or channel.megagroup:
                    channel = int(f'-100{channel.id}')
            except Exception:
                await context.edit(error_msg)
                return
        try:
            redis.delete(f"{redis_name}." + str(channel))
        except:
            await context.edit('emm...当前对话不存在于自动转发列表中。')
            return
        await context.edit(f"❌ 已关闭监控")
        await bot.send_message(int(ID_BOT), "❌ 已关闭线报监控")
        await log(f"监控已关闭")
    else:
        await context.edit(f"{lang('error_prefix')}{lang('arg_error')}")
        return

@listener(is_plugin=False, incoming=True, ignore_edited=True)
async def shift_channel_message(context):
    """ Event handler to auto forward channel messages. """
    if not redis_status():
        return
    if not redis.get("bot." + str(context.chat_id)):
        return

    ## 定义监控范围（由消息发送者id组成的数组）  群bot 没有感情的通知机器
    msg_sender_id = context.from_id.user_id
    msg_sender_id = str(msg_sender_id)
    if msg_sender_id not in ID_ARRAY:
        return

    ## 匹配带有执行命令的消息且原消息不能为空
    text = context.text
    if text != '' and '`' in text:
        text = text.split('`')[1]
    else:
        return

    ## 去解析命令
    results = await filters(text)
    if not results:
        return

    ## 向用户配置的容器Bot发送处理后的内容
    Botid = redis.get("bot." + str(context.chat_id))
    if Botid and results != '':
        await bot.send_message(int(Botid.decode()), results)


## ⬆️ 不懂勿动 ⬆️