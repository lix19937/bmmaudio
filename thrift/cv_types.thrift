include "base.thrift"

namespace py  cv_types
namespace go  cv_types
namespace cpp cv_types
namespace js  cv_types

/* 道玄: Vision Util Types */
// 定义图像相关数据类型
struct Point {
    1: double x, // [0, 1] represents width/columns
    2: double y, // [0, 1] represents height/rows
}

struct ImageInfo {
    // 优先用image_data, 没有则从image_url下载
    1: string image_url,
    2: optional binary image_data,
}

enum BoxTag {
    // 为每个服务写自己的box enum
    class_01 = 0,
    class_02 = 1,
}

struct BoundingBox {
    1: Point p1,
    2: Point p2,
    3: optional i32 width,
    4: optional i32 height,
    5: optional double prob,
    6: optional BoxTag tag,
}

enum ImageFormat {
    JPG = 0,
    PNG = 1,
    WEBP = 2,
}

struct JpgParam {
    // from 0 to 100 (the higher is the better). Default value is 95.
    1: optional i32 quality = 95,
}

struct PngParam {
    // compression level ( CV_IMWRITE_PNG_COMPRESSION ) from 0 to 9.
    // A higher value means a smaller size and longer compression time.
    // Default value is 3.
    1: optional i32 level = 3,
}

struct WebpParam {
    // from 1 to 100 (the higher is the better). Default value is 100.
    1: optional i32 quality = 100,
}

struct ImageSpec {
    1: optional ImageInfo image,

    // expected width of the output image in pixels
    2: optional i32 output_width,
    // expected height of the output image in pixels
    3: optional i32 output_height,

    // expected format of the output image
    4: optional ImageFormat output_format,
    5: optional JpgParam jpg_param,
    6: optional PngParam png_param,
    7: optional WebpParam webp_param,
}

struct ModelVersion {
    1: string model_version,
}

/* 道玄: Services Util Types:
* 1. Utils
* 2. Classification
* 3. Segmentation
* 4. Detection
* 5. Recognition
* 6. Joints Estimation
* 7. Inpainting
* 8。 Other */

// 道玄：Utils
struct ModelVersionReq {
    1: optional string status,
    255: optional base.Base Base,
}

struct ModelVersionRsp {
    1: ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

exception VisionException {
    1: string url,
    2: string error_msg,
}

// 道玄: Classification
struct TagPredict {
    1: i32 tag_id,
    2: double prob,
    3: optional string tag_name,
    4: optional string model_name,
    5: optional map<string, string> extra,
    6: optional list<Point> points,
    7: optional double norm_prob,
}

struct TagPredictResult {
    1: list<TagPredict> predicts,
    2: list<double> embeding,
}

struct ImagePredictReq {
    1: ImageInfo image,
    2: optional map<string,string> extra,
    255: optional base.Base Base,
}

struct VideoPredictReq {
    // 优先用frames, 没有则下载video_url并抽帧
    1: string video_url,
    2: optional list<ImageInfo> frames,
    3: optional map<string,string> extra,
    255: optional base.Base Base,
}

struct GifPredictReq {
    // 优先用frames, 没有则下载video_url并抽帧
    1: string gif_url,
    2: optional list<ImageInfo> frames,
    3: optional map<string,string> extra,
    255: optional base.Base Base,
}

struct VideoTagPredictRsp {
    1: list<TagPredictResult> predict_results,
    2: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

struct ImageTagPredictRsp {
    1: TagPredictResult predict_result,
    2: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

// 道玄: Segmentation
// thrift不支持继承，所有的Req复用classification中的请求
struct VideoSegRsp {
    1: list<list<BoundingBox>> boxes,
    2: list<binary> masks,
    3: map<i32,string> class_map,
    4: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

struct ImageSegRsp {
    1: list<BoundingBox> boxes,
    2: binary mask,
    3: map<i32,string> class_map,
    4: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

// 道玄: Detection
struct ImageDetRsp {
    1: list<BoundingBox> result,
    2: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

struct VideoDetRsp {
    1: list<list<BoundingBox>> results,
    2: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

// 道玄: Recognition
enum FaceExpTypes {
    neutral = 0,
    angry = 1,
    disgust = 2,
    fear = 3,
    happy = 4,
    sad = 5,
    surprise = 6,
}

struct ImageFaceRsp {
    1: list<FaceExpTypes> result,
    2: list<BoundingBox> bboxes,  // 顺序一致
    3: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

struct VideoFaceRsp {
    1: list<list<FaceExpTypes>> results,
    2: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

// 道玄: Joints Estimation
enum AccLevel {
    facial_5 = 5,
    facial_poor = 68,
    facial_mid = 106,
    facial_rich = 144,
    body_poor = 16,
    body_rich = 59,
}

struct ImageJointRsp {
    1: list<FaceExpTypes> result,
    2: list<AccLevel> joint_type,
    3: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

struct VideoJointRsp {
    1: list<list<FaceExpTypes>> results,
    2: list<list<AccLevel>> joint_types,
    3: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

// 道玄: Inpainting
struct DetectAndEraseReq {
    1: list<ImageSpec> images,
    2: optional map<string,string> extra,
    255: optional base.Base Base,
}

struct DetectAndEraseRsp {
    1: list<ImageInfo> images,
    2: list<list<BoundingBox>> boxes,
    200: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

struct ImageInpaintSpec {
    1: ImageSpec spec,
    // 默认为假，用传入的mask；为真用BBox生成mask
    2: bool use_boxes,
    3: optional ImageInfo mask,
    4: optional list<BoundingBox> boxes,
}

struct ImagesInpaintReq {
    1: list<ImageInpaintSpec> specs,
    4: optional map<string,string> extra,
    255: optional base.Base Base,
}

struct ImagesInpaintRsp {
    1: list<ImageInfo> images,
    200: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}

// 道玄: Other
struct ImageJsonReq {
    1: string json_script,
    255: optional base.Base Base,
}

struct ImageJsonRsp {
    1: string json_script,
    255: optional base.BaseResp BaseResp,
}

//
struct SpeechInfo{
   // speech_data, 没有则从 speech_url 下载
    1: string speech_url,  // http/https
    2: string speech_path, //local_path
    3: optional string debug_path,
    4: optional binary speech_data,
}

// speech  SpeechPredictReq
struct SpeechPredictReq {
    1: SpeechInfo info,
    2: optional map<string, string> extra,
    255: optional base.Base Base,
}

struct Fragment{
    1: string label,
    2: i64 time_begin,
    3: i64 time_end,
}

struct SpeechDetRsp {
    1: string json_str,
    2: optional list<list<Fragment>> results,
    3: optional ModelVersion model_version,
    255: optional base.BaseResp BaseResp,
}
