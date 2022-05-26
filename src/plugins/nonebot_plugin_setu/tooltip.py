
class Tooltip:
    EXCEED_MAXIMUM_TEXT_TEMPLATE: str = "一次最多只能发送%s张涩图哦"
    SEARCH_PATTERN_ERROR_TEXT_TEMPLATE: str = "没有“#%s”这个选项哦，请输入正确的选项"
    NO_SETU_ERROR_TEXT_TEMPLATE: str = "没有找到有关 %s 的涩图，请试试别的关键词"
    NO_PAINTER_ERROR_TEXT_TEMPLATE: str = "没有找到名为“%s”的画师"
    BELOW_MINIMUM_TEXT: str = "获取的涩图数量至少为一张"
    RANGE_ERROR_TEXT: str = "输入的范围错误，请输入正确的范围"
    RANKING_ARGUMENTS_ERROR_TEXT: str = "排行榜的参数错误，请输入正确的参数（日榜、周榜、月榜）"
    CONNECT_TIMEOUT_ERROR_TEXT: str = "现在网络不太稳定，请稍后再试"
    SEARCH_SETU_LOADING_TEXT: str = "正在搜索图片，请稍等..."
    SEARCH_SETU_INTERRUPT_TEXT: str = "已结束此处查询"
    LIMITED_TEXT: str = "今天发送的涩图已经达到上限了，请明天再来吧"
    COOLING_TEXT: str = "阿伟你又在看涩图喔，休息一下吧"