"""
Maya动画曲线生成器 v3.0
动态参数面板 — 每种曲线类型只显示其专属参数
Maya 2025 优化版本
"""

import maya.cmds as cmds
import maya.mel as mel
import math
from enum import Enum


class CurveType(Enum):
    SINE = 0
    COSINE = 1
    TRIANGLE = 2
    SQUARE = 3
    SAWTOOTH = 4
    REVERSE_SAWTOOTH = 5
    BOUNCE = 6
    CARD_SPRING = 7
    NOISE = 8
    RANDOM_STEP = 9
    S_CURVE = 10
    EXPONENTIAL = 11
    DAMPED_OSCILLATION = 12

    @classmethod
    def get_display_names(cls):
        return [
            "正弦波 (Sine)",
            "余弦波 (Cosine)",
            "三角波 (Triangle)",
            "方波 (Square)",
            "锯齿波 (Sawtooth)",
            "反向锯齿 (Reverse Sawtooth)",
            "弹跳 (Bounce)",
            "立牌弹起 (Card Spring)",
            "噪声 (Noise)",
            "随机步进 (Random Step)",
            "S曲线 (S-Curve)",
            "指数曲线 (Exponential)",
            "阻尼振荡 (Damped Oscillation)"
        ]

    @classmethod
    def from_index(cls, index):
        """通过 optionMenu 的 select 索引获取枚举（安全转换）"""
        try:
            return cls(index)
        except ValueError:
            return cls.SINE


class AnimationCurveGenerator:
    # 模式默认参数
    DEFAULTS = {
        "min_val": 0.0,
        "max_val": 90.0,
        "exponent": 2.0,
        "bounce_damping": 0.7,
        "card_overshoot": 0.3,
        "damp_target": 0.0,
        "damp_amplitude": 90.0,
        "damp_factor": 5.0,
    }

    def __init__(self):
        self.window_name = "curveGeneratorWindow"
        self._param_controls = {}

    # ────────────────────── UI 构建 ──────────────────────

    def create_ui(self):
        """创建主 UI 界面"""
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)

        start_frame = cmds.playbackOptions(query=True, minTime=True)
        end_frame = cmds.playbackOptions(query=True, maxTime=True)

        window = cmds.window(
            self.window_name,
            title="动画曲线生成器 v3.0",
            widthHeight=(380, 520),
            sizeable=True
        )
        cmds.columnLayout(adjustableColumn=True, rowSpacing=8)

        # ===== 目标 =====
        cmds.frameLayout(label="目标", collapsable=False)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        cmds.rowLayout(numberOfColumns=3, columnWidth3=(150, 140, 60), height=22)
        self.obj_field = cmds.textField(text="")
        cmds.button(label="获取选中", height=20, command=self.get_selected_object)
        cmds.button(label="?", width=20, height=20, command=self.show_help)
        cmds.setParent("..")

        cmds.rowLayout(numberOfColumns=2, columnWidth2=(100, 250), height=22)
        cmds.text(label="目标属性:", align="right")
        self.attr_menu = cmds.optionMenu(height=20)
        for attr in ["rotateX", "rotateY", "rotateZ",
                      "translateX", "translateY", "translateZ",
                      "scaleX", "scaleY", "scaleZ"]:
            cmds.menuItem(label=attr)
        cmds.setParent("..")
        cmds.setParent("..")
        cmds.setParent("..")

        # ===== 曲线类型 =====
        cmds.frameLayout(label="曲线类型", collapsable=False)
        self.curve_type = cmds.optionMenu(
            label="", height=22,
            changeCommand=self._on_curve_type_changed
        )
        for name in CurveType.get_display_names():
            cmds.menuItem(label=name)
        cmds.setParent("..")

        # ===== 动态参数区 =====
        self._params_frame = cmds.frameLayout(label="模式参数", collapsable=False)
        self._params_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=4)
        cmds.setParent("..")
        cmds.setParent("..")

        # 初始构建一次
        self._build_mode_params()

        # ===== 通用参数 =====
        cmds.frameLayout(label="通用参数", collapsable=False)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

        cmds.rowLayout(numberOfColumns=4, columnWidth4=(60, 100, 60, 100), height=22)
        cmds.text(label="起始:", align="right")
        self.start_time = cmds.floatField(value=start_frame, precision=1, minValue=0)
        cmds.text(label="结束:", align="right")
        self.end_time = cmds.floatField(value=end_frame, precision=1, minValue=0)
        cmds.setParent("..")

        cmds.button(label="使用当前时间轴范围", height=20, command=self.set_timeline_range)

        cmds.rowLayout(numberOfColumns=4, columnWidth4=(60, 100, 60, 100), height=22)
        cmds.text(label="循环:", align="right")
        self.loop_count = cmds.floatField(value=2.0, precision=1, minValue=0.5)
        cmds.text(label="密度:", align="right")
        self.key_count = cmds.intField(value=60, minValue=2, maxValue=2000)
        cmds.setParent("..")

        cmds.rowLayout(numberOfColumns=2, columnWidth2=(180, 180), height=20)
        self.reverse = cmds.checkBox(label="反向", value=False)
        self.auto_tangent = cmds.checkBox(label="自动平滑切线", value=True)
        cmds.setParent("..")

        cmds.setParent("..")

        # ===== 操作按钮 =====
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(180, 180), height=36)
        cmds.button(label="生成曲线", command=self.generate_curve)
        cmds.button(label="清除关键帧", command=self.clear_keys)
        cmds.setParent("..")

        # ===== 状态栏 =====
        self.status_text = cmds.text(
            label=f"就绪 | 时间轴: {int(start_frame)}-{int(end_frame)}",
            align="center", font="smallPlainLabelFont"
        )

        cmds.showWindow(window)

    # ────────────────────── 动态参数面板 ──────────────────────

    def _on_curve_type_changed(self, *args):
        """曲线类型切换回调"""
        self._build_mode_params()

    def _clear_layout(self, layout_name):
        """清空 layout 的所有子控件"""
        if cmds.layout(layout_name, exists=True):
            children = cmds.layout(layout_name, query=True, childArray=True) or []
            for child in children:
                cmds.deleteUI(child)

    def _build_mode_params(self, *args):
        """根据当前曲线类型重建参数面板"""
        # 保存当前 parent，构建完成后恢复
        saved_parent = cmds.setParent(query=True)

        self._clear_layout(self._params_layout)
        self._param_controls = {}

        curve_enum = self._get_current_curve_type()
        cmds.setParent(self._params_layout)

        if curve_enum == CurveType.DAMPED_OSCILLATION:
            self._build_damped_params()
        elif curve_enum == CurveType.BOUNCE:
            self._build_bounce_params()
        elif curve_enum == CurveType.CARD_SPRING:
            self._build_card_spring_params()
        elif curve_enum == CurveType.EXPONENTIAL:
            self._build_exponential_params()
        else:
            self._build_range_params()

        # 恢复 parent 上下文
        cmds.setParent(saved_parent)

    def _build_range_params(self):
        """范围类曲线：最小值 / 最大值"""
        cmds.rowLayout(numberOfColumns=4, columnWidth4=(60, 100, 60, 100), height=22)
        cmds.text(label="最小值:", align="right")
        self._param_controls["min_val"] = cmds.floatField(
            value=self.DEFAULTS["min_val"], precision=2)
        cmds.text(label="最大值:", align="right")
        self._param_controls["max_val"] = cmds.floatField(
            value=self.DEFAULTS["max_val"], precision=2)
        cmds.setParent("..")

    def _build_bounce_params(self):
        """弹跳：最小值 / 最大值 / 衰减"""
        self._build_range_params()
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(60, 100, 160), height=22)
        cmds.text(label="衰减:", align="right")
        self._param_controls["bounce_damping"] = cmds.floatField(
            value=self.DEFAULTS["bounce_damping"], precision=2,
            minValue=0.1, maxValue=1.0)
        cmds.text(label="(0.1=快衰减 1.0=不衰减)", font="smallPlainLabelFont")
        cmds.setParent("..")

    def _build_card_spring_params(self):
        """立牌弹起：最小值 / 最大值 / 阻尼"""
        self._build_range_params()
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(60, 100, 160), height=22)
        cmds.text(label="过冲:", align="right")
        self._param_controls["card_overshoot"] = cmds.floatField(
            value=self.DEFAULTS["card_overshoot"], precision=2,
            minValue=0.0, maxValue=0.8)
        cmds.text(label="(0=无过冲 0.8=大回弹)", font="smallPlainLabelFont")
        cmds.setParent("..")

    def _build_exponential_params(self):
        """指数：最小值 / 最大值 / 指数"""
        self._build_range_params()
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(60, 100, 160), height=22)
        cmds.text(label="指数:", align="right")
        self._param_controls["exponent"] = cmds.floatField(
            value=self.DEFAULTS["exponent"], precision=2,
            minValue=0.5, maxValue=5.0)
        cmds.text(label="(>1=加速 <1=减速)", font="smallPlainLabelFont")
        cmds.setParent("..")

    def _build_damped_params(self):
        """阻尼振荡：目标值 / 初始幅度 / 阻尼系数"""
        cmds.rowLayout(numberOfColumns=4, columnWidth4=(60, 100, 60, 100), height=22)
        cmds.text(label="目标值:", align="right")
        self._param_controls["damp_target"] = cmds.floatField(
            value=self.DEFAULTS["damp_target"], precision=2)
        cmds.text(label="幅度:", align="right")
        self._param_controls["damp_amplitude"] = cmds.floatField(
            value=self.DEFAULTS["damp_amplitude"], precision=2, minValue=0.0)
        cmds.setParent("..")

        cmds.rowLayout(numberOfColumns=3, columnWidth3=(60, 100, 160), height=22)
        cmds.text(label="阻尼:", align="right")
        self._param_controls["damp_factor"] = cmds.floatField(
            value=self.DEFAULTS["damp_factor"], precision=2,
            minValue=0.5, maxValue=30.0)
        cmds.text(label="(越大收敛越快, 典型3-10)", font="smallPlainLabelFont")
        cmds.setParent("..")

    # ────────────────────── UI 回调 ──────────────────────

    def _get_current_curve_type(self):
        idx = cmds.optionMenu(self.curve_type, query=True, select=True) - 1
        return CurveType.from_index(idx)

    def set_timeline_range(self, *args):
        start = cmds.playbackOptions(query=True, minTime=True)
        end = cmds.playbackOptions(query=True, maxTime=True)
        cmds.floatField(self.start_time, edit=True, value=start)
        cmds.floatField(self.end_time, edit=True, value=end)
        self.update_status(f"时间轴: {int(start)}-{int(end)}")

    def get_selected_object(self, *args):
        sel = cmds.ls(selection=True)
        if sel:
            cmds.textField(self.obj_field, edit=True, text=sel[0])
            self.update_status(f"已选: {sel[0]}")
        else:
            self.update_status("未选中任何对象")

    def get_target_object(self):
        name = cmds.textField(self.obj_field, query=True, text=True).strip()
        if not name:
            sel = cmds.ls(selection=True)
            if sel:
                name = sel[0]
                cmds.textField(self.obj_field, edit=True, text=name)
            else:
                self.update_status("请指定目标对象")
                return None
        return name

    def get_target_attribute(self):
        return cmds.optionMenu(self.attr_menu, query=True, value=True)

    def update_status(self, message):
        cmds.text(self.status_text, edit=True, label=message)

    def _read_param(self, key):
        """安全读取动态参数控件的值"""
        ctrl = self._param_controls.get(key)
        if ctrl and cmds.control(ctrl, exists=True):
            return cmds.floatField(ctrl, query=True, value=True)
        return self.DEFAULTS.get(key, 0.0)

    # ────────────────────── 曲线计算 ──────────────────────

    def calculate_bounce_value(self, t, loop_count, min_val, max_val, damping):
        if t == 0:
            return min_val
        bounce_count = max(int(loop_count), 1)
        bounce_duration = 1.0 / bounce_count
        bounce_index = min(int(t / bounce_duration), bounce_count - 1)
        local_t = (t - bounce_index * bounce_duration) / bounce_duration
        decay = damping ** bounce_index
        bounce_value = math.sin(local_t * math.pi) * decay
        result = min_val + (max_val - min_val) * bounce_value
        return max(min_val, min(max_val, result))

    def calculate_card_spring_value(self, t, min_val, max_val, overshoot):
        if t == 0:
            return min_val
        if t >= 1:
            return max_val
        frequency = 3.0 + (1.0 - overshoot) * 2.0
        angle = t * frequency * math.pi / 2
        decay_factor = math.exp(-t * 3.0 * (1.0 + overshoot * 2.0))
        oscillation = math.sin(angle) * decay_factor
        overshoot_amount = overshoot * 0.3
        base_curve = 1 - math.exp(-t * 4.0 * (1.0 + overshoot))
        value = max(0, min(1, base_curve + oscillation * overshoot_amount))
        return min_val + (max_val - min_val) * value

    def calculate_damped_oscillation_value(self, t, target, amplitude, damping, frequency):
        if t >= 1:
            return target
        envelope = math.exp(-damping * t)
        oscillation = math.cos(frequency * t * 2 * math.pi)
        return target + amplitude * envelope * oscillation

    def _hash_noise(self, x):
        x = int(x * 100000)
        x = ((x >> 13) ^ x) * 1234567
        x = (x * (x * x * 15731 + 789221) + 1376312589) & 0x7fffffff
        return x / 0x7fffffff

    def calculate_curve_value(self, t, curve_enum, loop_count, params):
        """统一计算入口，params 字典包含所有模式参数"""
        min_val = params.get("min_val", 0.0)
        max_val = params.get("max_val", 90.0)

        # 阻尼振荡：绝对参数，不走 min/max 映射
        if curve_enum == CurveType.DAMPED_OSCILLATION:
            return self.calculate_damped_oscillation_value(
                t,
                params.get("damp_target", 0.0),
                params.get("damp_amplitude", 90.0),
                params.get("damp_factor", 5.0),
                loop_count
            )

        period = 1.0 / loop_count
        phase = t / period
        phase_norm = phase % 1.0

        if curve_enum == CurveType.CARD_SPRING:
            value = self.calculate_card_spring_value(
                t, 0, 1, params.get("card_overshoot", 0.3))
        elif curve_enum == CurveType.BOUNCE:
            value = self.calculate_bounce_value(
                t, loop_count, 0, 1, params.get("bounce_damping", 0.7))
            value = max(0, min(1, value))
        elif curve_enum == CurveType.SINE:
            value = (math.sin(phase * 2 * math.pi) + 1) / 2
        elif curve_enum == CurveType.COSINE:
            value = (math.cos(phase * 2 * math.pi) + 1) / 2
        elif curve_enum == CurveType.TRIANGLE:
            value = 2 * abs(phase_norm - 0.5)
        elif curve_enum == CurveType.SQUARE:
            value = 1 if phase_norm < 0.5 else 0
        elif curve_enum == CurveType.SAWTOOTH:
            value = phase_norm
        elif curve_enum == CurveType.REVERSE_SAWTOOTH:
            value = 1 - phase_norm
        elif curve_enum == CurveType.NOISE:
            value = self._hash_noise(phase)
        elif curve_enum == CurveType.RANDOM_STEP:
            value = self._hash_noise(int(phase_norm * 100))
        elif curve_enum == CurveType.S_CURVE:
            value = 1 / (1 + math.exp(-(phase_norm - 0.5) * 10))
        elif curve_enum == CurveType.EXPONENTIAL:
            exp = params.get("exponent", 2.0)
            value = phase_norm ** exp
        else:
            value = phase_norm

        return min_val + (max_val - min_val) * value

    # ────────────────────── 关键帧操作 ──────────────────────

    def clear_keys_for_object(self, obj_name, attr_name):
        if not cmds.objExists(obj_name):
            return False
        try:
            key_times = cmds.keyframe(obj_name, attribute=attr_name, query=True, timeChange=True)
            if key_times:
                cmds.cutKey(obj_name, attribute=attr_name,
                            time=(min(key_times), max(key_times)), clear=True)
                return True
        except Exception as e:
            cmds.warning(f"清除关键帧失败: {e}")
        return False

    def _get_reverse_center(self, curve_enum, params):
        """获取反向的中心值"""
        if curve_enum == CurveType.DAMPED_OSCILLATION:
            return params.get("damp_target", 0.0)
        return (params.get("min_val", 0.0) + params.get("max_val", 90.0)) / 2.0

    def generate_curve(self, *args):
        obj_name = self.get_target_object()
        if not obj_name:
            return
        attr_name = self.get_target_attribute()
        curve_enum = self._get_current_curve_type()

        try:
            start_time = cmds.floatField(self.start_time, query=True, value=True)
            end_time = cmds.floatField(self.end_time, query=True, value=True)
            key_count = cmds.intField(self.key_count, query=True, value=True)
            loop_count = cmds.floatField(self.loop_count, query=True, value=True)
            reverse = cmds.checkBox(self.reverse, query=True, value=True)
            auto_tangent = cmds.checkBox(self.auto_tangent, query=True, value=True)
        except Exception as e:
            self.update_status(f"参数读取失败: {e}")
            return

        # 读取动态参数
        params = {}
        for key in self._param_controls:
            params[key] = self._read_param(key)

        if start_time >= end_time:
            self.update_status("起始必须小于结束")
            return
        if key_count < 2:
            self.update_status("密度必须≥2")
            return
        if not cmds.objExists(obj_name):
            self.update_status(f"对象 '{obj_name}' 不存在")
            return

        full_attr = f"{obj_name}.{attr_name}"
        if not cmds.objExists(full_attr):
            self.update_status(f"属性 '{attr_name}' 不存在")
            return

        reverse_center = self._get_reverse_center(curve_enum, params) if reverse else None

        cmds.undoInfo(openChunk=True)
        try:
            # 先清除旧关键帧
            self.clear_keys_for_object(obj_name, attr_name)

            self.update_status("生成中...")

            time_step = (end_time - start_time) / (key_count - 1)
            for i in range(key_count):
                t = start_time + i * time_step
                t_norm = (t - start_time) / (end_time - start_time)

                value = self.calculate_curve_value(t_norm, curve_enum, loop_count, params)

                if reverse_center is not None:
                    value = 2 * reverse_center - value

                cmds.setKeyframe(obj_name, attribute=attr_name, time=t, value=value)

            if auto_tangent:
                try:
                    cmds.selectKey(obj_name, attribute=attr_name, time=(start_time, end_time))
                    mel.eval('keyTangent -edit -tangentType "spline"')
                    cmds.select(clear=True)
                except Exception as e:
                    cmds.warning(f"切线设置失败: {e}")

            self.update_status(f"已生成 {key_count} 帧到 {full_attr}")
            try:
                mel.eval('refreshAE')
                mel.eval('GraphEditor')
            except Exception:
                pass

        except Exception as e:
            self.update_status(f"生成失败: {e}")
            cmds.warning(f"生成失败: {e}")
        finally:
            cmds.undoInfo(closeChunk=True)

    def clear_keys(self, *args):
        obj_name = self.get_target_object()
        if not obj_name:
            return
        attr_name = self.get_target_attribute()
        cmds.undoInfo(openChunk=True)
        try:
            if self.clear_keys_for_object(obj_name, attr_name):
                self.update_status(f"已清除 {obj_name}.{attr_name}")
            else:
                self.update_status("无关键帧可清除")
        except Exception as e:
            self.update_status(f"清除失败: {e}")
        finally:
            cmds.undoInfo(closeChunk=True)

    def show_help(self, *args):
        help_text = """===== 动画曲线生成器 v3.0 =====

核心参数:
  时间范围 — 关键帧的时间区间
  循环次数 — 波形在时间范围内重复几次（阻尼振荡=振荡频率）
  密度    — 关键帧数量
  反向    — 垂直翻转曲线（围绕中心值镜像）

曲线类型:
  正弦/余弦/三角波/方波/锯齿波 — 基础波形，参数: 最小值/最大值
  弹跳    — 物理弹跳衰减，参数: 最小值/最大值/衰减(0.1-1.0)
  立牌弹起 — 快速弹起后稳定，参数: 最小值/最大值/过冲(0-0.8)
  噪声/随机步进 — 随机值，参数: 最小值/最大值
  S曲线   — Sigmoid平滑过渡，参数: 最小值/最大值
  指数曲线 — 幂函数曲线，参数: 最小值/最大值/指数(0.5-5.0)
  阻尼振荡 — 围绕目标值摇摆并收敛
    参数: 目标值/初始幅度(绝对值)/阻尼系数(越大收敛越快)

反向说明:
  勾选后曲线围绕中心值垂直翻转
  例如: 0↔90 变成 90↔0; 阻尼振荡围绕目标值翻转
"""
        cmds.confirmDialog(title="帮助", message=help_text, button="确定")

    # ────────────────────── 入口 ──────────────────────

    def run(self):
        self.create_ui()


def create_curve_generator():
    gen = AnimationCurveGenerator()
    gen.run()
    return gen


if __name__ == "__main__":
    generator = create_curve_generator()
