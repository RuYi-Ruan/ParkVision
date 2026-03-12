"""detection 模块的接口视图。"""

from rest_framework.views import APIView

from common.response import api_response

from .serializers import DetectionRequestSerializer
from .services import detect_image, get_detection_module_info, list_detection_presets


class DetectionModuleView(APIView):
    """提供识别模块说明、预设列表和图片识别骨架接口。"""

    def get(self, request):
        # mode=module 用于快速检查接口是否挂载；默认返回识别预设列表。
        if request.query_params.get("mode") == "module":
            return api_response(get_detection_module_info())
        return api_response(data=list_detection_presets())

    def post(self, request):
        # 当前阶段先把上传动作打通，返回与未来 AI 推理兼容的结构。
        serializer = DetectionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image = serializer.validated_data.get("image")
        preset_id = serializer.validated_data.get("preset_id", "")
        file_name = image.name if image else ""
        result = detect_image(file_name=file_name, preset_id=preset_id)
        return api_response(data=result, message="detect success")
