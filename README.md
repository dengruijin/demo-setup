## otopi开发示例

### 开发环境

CentOS-7.X

安装依赖包：

```
rpm -ivh https://resources.ovirt.org/pub/ovirt-4.3/rpm/el7/noarch/otopi-common-1.8.4-1.el7.noarch.rpm
rpm -ivh https://resources.ovirt.org/pub/ovirt-4.3/rpm/el7/noarch/python2-otopi-1.8.4-1.el7.noarch.rpm
```

说明：

``otopi-common``的作用：

- 在``/usr/share/otopi/plugins/``目录中提供``otopi``的基础插件
- 提供可执行脚本：``/usr/sbin/otopi``，这是``otopi``的入口
- 提供辅助脚本: ``/usr/share/otopi/otopi-functions``

``python2-otopi``的作用：

- 提供``otopi``的python库：``/usr/lib/python2.7/site-packages/otopi/``

如果不想装rpm包，也可以把这些插件和库文件放到自己的工程目录中。

### 工程创建

- 创建工程目录

  创建一个工程目录(本例为``demo-setup``目录)，并在该目录下创建如下子目录：

  ```shell
  mkdir -p ~/demo-setup/otopi-plugins/installer
  ```

- 编写入口文件

  ```shell
  cd ~/demo-setup
  touch demo-setup && chmod +x demo-setup 
  vi demo-setup # 编辑入口脚本
  ```

  内容如下:

  ```shell
  #!/bin/sh
  
  scriptdir="$(dirname "$0")"
  otopidir="${scriptdir}"
  extraenv=""
  
  if [ -x "${scriptdir}/otopi" ]; then
          otopidir="${scriptdir}"
  else
          otopidir="/usr/sbin"
  fi
  
  extraenv="\"PREPEND:BASE/pluginPath=str:${scriptdir}/otopi-plugins\""
  exec "${otopidir}/otopi" "${extraenv} APPEND:BASE/pluginGroups=str:installer:$*"
  ```

  这个脚本就是对``/usr/sbin/otopi``脚本的封装，包括：

  - 指定插件路径``${scriptdir}/otopi-plugins``
  - 指定需要执行的插件组为``installer``

  

  从这里可以看出，我们要写的插件应该放在``otopi-plugins/installer``中。

  ``otopi``寻找插件组的路径默认是在``/usr/share/otopi/plugins/``，如果我们没有在``demo-setup``脚本中指定插件组位置为``${scriptdir}/otopi-plugins``那我们可以把``installer``插件组放到``/usr/share/otopi/plugins/``中。

  同样，如果在前面没有装``otopi-common``和``python2-otopi``包，那也可以把``otopi``这个核心插件组放在``${scriptdir}/otopi-plugins``下面，把``/usr/sbin/otopi``和``/usr/share/otopi/otopi-functions``脚本放工程目录,把``/usr/lib/python2.7/site-packages/otopi/``放在工程目录的``pythonlib``目录下，并在工程目录下创建一个空文件``.bundled``来告诉``otopi``在工程目录中寻找基础插件库。

- 编写一个简单的自定义插件

  编写一个名称为``confirm``的插件，作用是确认是否要执行配置工作。

  ```shell
  cd ~/demo-setup/installer/
  mkdir confirm
  vi confirm/__init__.py
  ```

  内容如下:

  ```python
  from otopi import util
  from . import prompt
  
  @util.export
  def createPlugins(context):
      prompt.Plugin(context=context)
  ```

  编辑``confirm/prompt.py ``内容如下:

  ```python
  from otopi import constants
  from otopi import plugin
  from otopi import util
  
  @util.export
  class Plugin(plugin.PluginBase):
      def __init__(self, context):
          super(Plugin, self).__init__(context=context)
  
      @plugin.event(stage=plugin.Stages.STAGE_INIT)
      def _init(self):
          self.environment.setdefault('enabled', None)
  
  
      @plugin.event(
          stage=plugin.Stages.STAGE_CUSTOMIZATION,
          name="CONFIRM_INSTALL",
      )
      def _customization(self):
          if self.environment['enabled'] is None:
              self.environment['enabled'] = (
                  self.dialog.queryString(
                      name='CONFIRM_INSTALL_DIALOG',
                      note=('Setup demo program on this host (@VALUES@) [@DEFAULT@]: '),
                      prompt=True,
                      validValues=('Yes','No'),
                      caseSensitive=False,
                      default='Yes',
                  ) != 'no'
              )
  
      @plugin.event(
          stage=plugin.Stages.STAGE_MISC,
          name="MISC_INSTALL",
      )
      def _misc(self):
          self.dialog.note( text='enabled=%s' % self.environment['enabled'])
          self.logger.warn( 'enabled=%s' % self.environment['enabled'])
  ```

  

### 插件开发

#### Stage

- STAGE_BOOT 设置启动环境
- STAGE_INIT：初始化组件，或初始化环境变量
- **STAGE_SETUP**:  初始化环境变量
- STAGE_INTERNAL_PACKAGES: 安装setup自己以来的包
- **STAGE_PROGRAMS**: 检测本系统中可用的程序命令
- STAGE_LATE_SETUP,
- **STAGE_CUSTOMIZATION**: 用于交互式设置各自定义参数
- STAGE_VALIDATION,
- STAGE_TRANSACTION_BEGIN,
- STAGE_EARLY_MISC,
- **STAGE_PACKAGES**：安装程序需要的包
- **STAGE_MISC**: 装包之后的各种配置操作
- **STAGE_TRANSACTION_END**: 事务提交
- STAGE_CLOSEUP,
- STAGE_CLEANUP,
- STAGE_PRE_TERMINATE,
- **STAGE_TERMINATE**: 结束
- STAGE_REBOOT
