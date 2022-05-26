
from types import ModuleType
from typing import Optional, Any, List, Callable, Type, Union
from datetime import datetime
from contextlib import AsyncExitStack
from nonebot.log import logger
from nonebot.rule import Rule
from nonebot.typing import T_Handler, T_State, T_DependencyCache, T_TypeUpdater, T_PermissionUpdater
from nonebot.plugin import Plugin
from nonebot.matcher import Matcher, matchers
from nonebot.adapters import Bot, Event
from nonebot.permission import Permission
from nonebot.exception import FinishedException, RejectedException, PausedException
from nonebot.dependencies import Dependent


class MyMatcher(Matcher):

    befoer_handler: Optional[Dependent[Any]] = None
    after_handler: Optional[Dependent[Any]] = None

    def __init__(self):
        super().__init__()

    @classmethod
    def new(
        cls,
        type_: str = "",
        rule: Optional[Rule] = None,
        permission: Optional[Permission] = None,
        handlers: Optional[List[Union[T_Handler, Dependent[Any]]]] = None,
        temp: bool = False,
        priority: int = 1,
        block: bool = False,
        *,
        plugin: Optional["Plugin"] = None,
        module: Optional[ModuleType] = None,
        expire_time: Optional[datetime] = None,
        default_state: Optional[T_State] = None,
        default_type_updater: Optional[Union[T_TypeUpdater, Dependent[str]]] = None,
        default_permission_updater: Optional[
            Union[T_PermissionUpdater, Dependent[Permission]]
        ] = None,
    ) -> Type["MyMatcher"]:
        """
        创建一个新的事件响应器，并存储至 `matchers <#matchers>`_

        参数:
            type_: 事件响应器类型，与 `event.get_type()` 一致时触发，空字符串表示任意
            rule: 匹配规则
            permission: 权限
            handlers: 事件处理函数列表
            temp: 是否为临时事件响应器，即触发一次后删除
            priority: 响应优先级
            block: 是否阻止事件向更低优先级的响应器传播
            plugin: 事件响应器所在插件
            module: 事件响应器所在模块
            default_state: 默认状态 `state`
            expire_time: 事件响应器最终有效时间点，过时即被删除

        返回:
            Type[Matcher]: 新的事件响应器类
        """
        NewMatcher = type(
            "MyMatcher",
            (MyMatcher,),
            {
                "plugin": plugin,
                "module": module,
                "plugin_name": plugin and plugin.name,
                "module_name": module and module.__name__,
                "type": type_,
                "rule": rule or Rule(),
                "permission": permission or Permission(),
                "handlers": [
                    handler
                    if isinstance(handler, Dependent)
                    else Dependent[Any].parse(
                        call=handler, allow_types=cls.HANDLER_PARAM_TYPES
                    )
                    for handler in handlers
                ]
                if handlers
                else [],
                "temp": temp,
                "expire_time": expire_time,
                "priority": priority,
                "block": block,
                "_default_state": default_state or {},
                "_default_type_updater": (
                    default_type_updater
                    if isinstance(default_type_updater, Dependent)
                    else default_type_updater
                    and Dependent[str].parse(
                        call=default_type_updater, allow_types=cls.HANDLER_PARAM_TYPES
                    )
                ),
                "_default_permission_updater": (
                    default_permission_updater
                    if isinstance(default_permission_updater, Dependent)
                    else default_permission_updater
                    and Dependent[Permission].parse(
                        call=default_permission_updater,
                        allow_types=cls.HANDLER_PARAM_TYPES,
                    )
                ),
            },
        )

        logger.trace(f"Define new matcher {NewMatcher}")

        matchers[priority].append(NewMatcher)

        return NewMatcher

    @classmethod
    def befoer_handle(
        cls, parameterless: Optional[List[Any]] = None
    ) -> Callable[[T_Handler], T_Handler]:

        def _decorator(fanc: T_Handler) -> T_Handler:

            handler_ = Dependent[Any].parse(
                call=fanc,
                parameterless=parameterless,
                allow_types=cls.HANDLER_PARAM_TYPES,
            )

            cls.befoer_handler = handler_
            cls.handlers.insert(0, handler_)

            return fanc

        return _decorator

    @classmethod
    def after_handle(
        cls, parameterless: Optional[List[Any]] = None
    ) -> Callable[[T_Handler], T_Handler]:

        def _decorator(fanc: T_Handler) -> T_Handler:

            handler_ = Dependent[Any].parse(
                call=fanc,
                parameterless=parameterless,
                allow_types=cls.HANDLER_PARAM_TYPES,
            )

            cls.after_handler = handler_

            return fanc

        return _decorator

    async def run(
        self,
        bot: Bot,
        event: Event,
        state: T_State,
        stack: Optional[AsyncExitStack] = None,
        dependency_cache: Optional[T_DependencyCache] = None,
    ):  

        if self.after_handler is not None and self.after_handler not in self.handlers:
            self.handlers.append(self.after_handler)

        try:
            await self.simple_run(bot, event, state, stack, dependency_cache)

        except RejectedException:
            await self.resolve_reject()
            type_ = await self.update_type(bot, event)
            permission = await self.update_permission(bot, event)
            user_id = event.get_user_id()

            self.state["user_id"] = user_id

            for i, m in enumerate(matchers[88]) if 88 in matchers else []:
                if m._default_state["user_id"] == user_id:
                    matchers[88].pop(i)

            MyMatcher.new(
                type_,
                Rule(),
                permission,
                self.handlers,
                temp=True,
                priority=88,
                block=True,
                plugin=self.plugin,
                module=self.module,
                expire_time=datetime.now() + bot.config.session_expire_timeout,
                default_state=self.state,
                default_type_updater=self.__class__._default_type_updater,
                default_permission_updater=self.__class__._default_permission_updater,
            )

        except PausedException:
            type_ = await self.update_type(bot, event)
            permission = await self.update_permission(bot, event)

            MyMatcher.new(
                type_,
                Rule(),
                permission,
                self.handlers,
                temp=True,
                priority=77,
                block=True,
                plugin=self.plugin,
                module=self.module,
                expire_time=datetime.now() + bot.config.session_expire_timeout,
                default_state=self.state,
                default_type_updater=self.__class__._default_type_updater,
                default_permission_updater=self.__class__._default_permission_updater,
            )

        except FinishedException:
            if self.after_handler is not None:
                self.handlers = [self.after_handler]
                await self.run(bot, event, state, stack, dependency_cache)
