
import sys
import inspect
from types import ModuleType
from typing import Optional, Union, List, Tuple, Set, Type
from nonebot.rule import Rule, command
from nonebot.typing import T_State, T_Handler, T_RuleChecker, T_PermissionChecker
from nonebot.plugin import _current_plugin
from nonebot.permission import Permission
from nonebot.dependencies import Dependent
from .my_matcher import MyMatcher


def _store_matcher(matcher: Type[MyMatcher]) -> None:
    plugin = _current_plugin.get()
    # only store the matcher defined in the plugin
    if plugin:
        plugin.matcher.add(matcher)


def _get_matcher_module(depth: int = 1) -> Optional[ModuleType]:
    current_frame = inspect.currentframe()
    if current_frame is None:
        return None
    frame = inspect.getouterframes(current_frame)[depth + 1].frame
    module_name = frame.f_globals["__name__"]
    return sys.modules.get(module_name)


def on_message(
    rule: Optional[Union[Rule, T_RuleChecker]] = None,
    permission: Optional[Union[Permission, T_PermissionChecker]] = None,
    *,
    handlers: Optional[List[Union[T_Handler, Dependent]]] = None,
    temp: bool = False,
    priority: int = 1,
    block: bool = True,
    state: Optional[T_State] = None,
    _depth: int = 0,
) -> Type[MyMatcher]:
    """
    注册一个消息事件响应器。

    参数:
        rule: 事件响应规则
        permission: 事件响应权限
        handlers: 事件处理函数列表
        temp: 是否为临时事件响应器（仅执行一次）
        priority: 事件响应器优先级
        block: 是否阻止事件向更低优先级传递
        state: 默认 state
    """
    matcher = MyMatcher.new(
        "message",
        Rule() & rule,
        Permission() | permission,
        temp=temp,
        priority=priority,
        block=block,
        handlers=handlers,
        plugin=_current_plugin.get(),
        module=_get_matcher_module(_depth + 1),
        default_state=state,
    )
    _store_matcher(matcher)
    return matcher


def on_command(
    cmd: Union[str, Tuple[str, ...]],
    rule: Optional[Union[Rule, T_RuleChecker]] = None,
    aliases: Optional[Set[Union[str, Tuple[str, ...]]]] = None,
    _depth: int = 0,
    **kwargs,
) -> Type[MyMatcher]:
    """
    注册一个消息事件响应器，并且当消息以指定命令开头时响应。

    命令匹配规则参考: `命令形式匹配 <rule.md#command-command>`_

    参数:
        cmd: 指定命令内容
        rule: 事件响应规则
        aliases: 命令别名
        permission: 事件响应权限
        handlers: 事件处理函数列表
        temp: 是否为临时事件响应器（仅执行一次）
        priority: 事件响应器优先级
        block: 是否阻止事件向更低优先级传递
        state: 默认 state
    """

    commands = set([cmd]) | (aliases or set())
    block = kwargs.pop("block", False)
    return on_message(
        command(*commands) & rule, block=block, **kwargs, _depth=_depth + 1
    )