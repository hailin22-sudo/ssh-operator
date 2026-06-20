# 宝塔 `bt` 命令速查表

宝塔面板安装后会在系统里注册 `bt` 命令，可在 SSH 中直接调用，无需登录 Web 面板。

## 常用命令

| 命令 | 作用 |
|---|---|
| `bt` | 显示交互式菜单 |
| `bt default` | 查看面板访问地址、用户名、密码 |
| `bt start` | 启动面板 |
| `bt stop` | 停止面板 |
| `bt restart` | 重启面板 |
| `bt reload` | 重载面板配置 |
| `bt 5` | 修改面板密码（交互式） |
| `bt 6` | 修改面板用户名（交互式） |
| `bt 10` | 查看面板日志 |
| `bt 12` | 取消域名绑定限制 |
| `bt 13` | 取消 IP 访问限制 |
| `bt 14` | 查看面板错误日志 |
| `bt 16` | 修改面板端口（交互式） |
| `bt 22` | 取消 SSL 强制 HTTPS |
| `bt 23` | 设置 SSL 证书 |

## 服务管理

```bash
bt reload nginx      # 重载 Nginx
bt restart nginx     # 重启 Nginx
bt reload apache     # 重载 Apache
bt restart apache    # 重启 Apache
bt restart mysql     # 重启 MySQL
bt restart php-fpm   # 重启 PHP-FPM
```

## 快速定位

```bash
# 面板端口
cat /www/server/panel/data/port.pl

# 面板安装目录
ls /www/server/panel/

# 网站 Nginx 配置目录
ls /www/server/panel/vhost/nginx/

# Nginx 错误日志
tail -f /www/wwwlogs/nginx_error.log

# 面板错误日志
tail -f /www/server/panel/logs/error.log
```

> 注：`bt` 命令子菜单编号会随版本变化，请以实际安装版本的输出为准。
