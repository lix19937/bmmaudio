//包含头文件
include "base.thrift"
include "cv_types.thrift"

//指定目标语言
namespace py cv_common
namespace go cv_common
namespace cpp cv_common
namespace js cv_common

/* 道玄: Services:
* 1. Classification
* 2. Segmentation
* 3. Detection
* 4. Recognition
* 5. Joints Estimation
* 6. Inpainting
* 7. Get Model Version
* 8. SpeechDetect
*/

//定义服务  注意 { 有空格     Thrift编译器会根据选择的目标语言为server产生服务接口代码，为client产生桩代码。
service VisionServices {
    cv_types.VideoTagPredictRsp Predict(1: cv_types.VideoPredictReq req) throws (1: cv_types.VisionException exp),
    cv_types.ImageSegRsp Seg(1: cv_types.ImagePredictReq req),
    cv_types.ImageDetRsp Detect(1: cv_types.ImagePredictReq req),
    cv_types.ImageFaceRsp Reg(1: cv_types.ImagePredictReq req),
    cv_types.ImageJointRsp Est(1: cv_types.ImagePredictReq req),//图像拼接
    cv_types.ImagesInpaintRsp Inpaint(1: cv_types.ImagesInpaintReq req),   //去瑕疵
    cv_types.ModelVersionRsp GetModelVersion(1: cv_types.ModelVersionReq req),
    cv_types.ImageJsonRsp RunJson(1: cv_types.ImageJsonReq req),
    cv_types.SpeechDetRsp SpeechDetect(1: cv_types.SpeechPredictReq req),  //音频分类
}
