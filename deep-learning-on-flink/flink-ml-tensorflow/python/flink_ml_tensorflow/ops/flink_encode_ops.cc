/* Copyright 2019 The flink-ai-extended Authors. All Rights Reserved.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#include "tensorflow/core/framework/op_kernel.h"
#include "tensorflow/core/framework/common_shape_fns.h"
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/shape_inference.h"
#include "tensorflow/core/util/example_proto_helper.h"
#include "tensorflow/core/example/example.pb.h"
using namespace tensorflow;
namespace tensorflow {

    class EncodeCSVOp: public OpKernel {
    public:
        explicit EncodeCSVOp(OpKernelConstruction *ctx) : OpKernel(ctx) {
            OP_REQUIRES_OK(ctx, ctx->GetAttr("INPUT_TYPE", &input_type_));
            OP_REQUIRES(ctx, input_type_.size() < std::numeric_limits<int>::max(),
                        errors::InvalidArgument("Input type too large"));
            OP_REQUIRES_OK(ctx, ctx->GetAttr("field_delim", &delim_));
            OP_REQUIRES(ctx, delim_.size() == 1,
                        errors::InvalidArgument("field_delim should be only 1 char"));
        }

        void Compute(OpKernelContext *ctx) override {
            OpInputList values;
            OP_REQUIRES_OK(ctx, ctx->input_list("records", &values));
            OpOutputList outputs;
            OP_REQUIRES_OK(ctx, ctx->output_list("output", &outputs));
            Tensor* out = nullptr;
            OP_REQUIRES_OK(ctx, outputs.allocate(0, values[0].shape(), &out));

            int64 records_size = values[0].dim_size(0);
            int column_size = values.size();
            int last_column_index = column_size - 1;
            for(int j = 0; j < records_size; j++) {
                std::string row;
                for (int i = 0; i < values.size(); i++) {
                    std::string item;
                    switch (input_type_[i]) {
                        case DT_INT32:
                            item = std::to_string(values[i].flat<int32>()(j));
                            break;
                        case DT_INT64:
                            item = std::to_string(values[i].flat<int64>()(j));
                            break;
                        case DT_FLOAT:
                            item = std::to_string(values[i].flat<float>()(j));
                            break;
                        case DT_DOUBLE:
                            item = std::to_string(values[i].flat<double>()(j));
                            break;
                        case DT_STRING:
                            item = values[i].flat<tstring>()(j);
                            break;
                        default:
                            item = values[i].flat<tstring>()(j);

                    }
                    row += item;
                    if(last_column_index != i){
                        row += delim_;
                    }
                }
                outputs[0]->flat<tstring>()(j) = row;
            }
        }

    private:
        std::vector<DataType> input_type_;
        std::string delim_;
    };

    class EncodeExampleOp: public OpKernel {
    public:
        explicit EncodeExampleOp(OpKernelConstruction *ctx) : OpKernel(ctx) {
            OP_REQUIRES_OK(ctx, ctx->GetAttr("INPUT_TYPE", &input_types_));
            OP_REQUIRES(ctx, input_types_.size() < std::numeric_limits<int>::max(),
                        errors::InvalidArgument("Input type too large"));
            OP_REQUIRES_OK(ctx, ctx->GetAttr("names", &input_names_));
            OP_REQUIRES(ctx, input_names_.size() == input_types_.size(),
                        errors::InvalidArgument("Input names must equal input list"));
        }
        void Compute(OpKernelContext *ctx) override {
            OpInputList values;
            OP_REQUIRES_OK(ctx, ctx->input_list("records", &values));
            OpOutputList outputs;
            OP_REQUIRES_OK(ctx, ctx->output_list("output", &outputs));
            Tensor* out = nullptr;
            OP_REQUIRES_OK(ctx, outputs.allocate(0, values[0].shape(), &out));
            int64 records_size = values[0].dim_size(0);
            int column_size = values.size();
            int last_column_index = column_size - 1;

            for(int j = 0; j <records_size; j++) {
                Example example;
                auto* feature_map = example.mutable_features()->mutable_feature();
                for (int i = 0; i < column_size; i++) {
                    switch (input_types_[i]) {
                        case DT_INT32: {
                            auto *field_list = (*feature_map)[input_names_[i]].mutable_int64_list();
                            field_list->add_value(values[i].flat<int32>()(j));
                            break;
                        }
                        case DT_INT64: {
                            auto *field_list = (*feature_map)[input_names_[i]].mutable_int64_list();
                            field_list->add_value(values[i].flat<int64>()(j));
                            break;
                        }
                        case DT_FLOAT: {
                            auto *field_list = (*feature_map)[input_names_[i]].mutable_float_list();
                            field_list->add_value(values[i].flat<float>()(j));
                            break;
                        }
                        case DT_DOUBLE: {
                            auto *field_list = (*feature_map)[input_names_[i]].mutable_float_list();
                            field_list->add_value((float)(values[i].flat<double>()(j)));
                            break;
                        }
                        case DT_STRING: {
                            auto *field_list = (*feature_map)[input_names_[i]].mutable_bytes_list();
                            field_list->add_value(values[i].flat<tstring>()(j));
                            break;
                        }
                        default: {
                            auto *field_list = (*feature_map)[input_names_[i]].mutable_bytes_list();
                            field_list->add_value(values[i].flat<tstring>()(j));
                            break;
                        }

                    }
                }
                outputs[0]->flat<tstring>()(j) = example.SerializeAsString();
            }
        }

    private:
        std::vector<DataType> input_types_;
        std::vector<std::string> input_names_;
    };

}// namespace tensorflow

using tensorflow::shape_inference::DimensionHandle;
using tensorflow::shape_inference::InferenceContext;
using tensorflow::shape_inference::ShapeHandle;

REGISTER_OP("EncodeCSV")
        .Input("records: INPUT_TYPE")
        .Output("output: string")
        .Attr("INPUT_TYPE: list({float,double,int32,int64,string})")
        .Attr("field_delim: string=','")
        .SetShapeFn([](InferenceContext *c) {
            std::vector<ShapeHandle> input_handles;
            c->input("records", &input_handles);
            if(!input_handles.empty()) {
                for(int i = 0; i < input_handles.size(); i++){
                    ShapeHandle v = input_handles[i];
                    ShapeHandle vv;
                    TF_RETURN_IF_ERROR(c->WithRank(v, 1, &vv));
                }
                c->set_output(0, input_handles[0]);
                return Status::OK();
            } else{
                return errors::Internal("must input tensor to decode");
            }
        });

REGISTER_KERNEL_BUILDER(Name("EncodeCSV").Device(DEVICE_CPU), EncodeCSVOp);

REGISTER_OP("EncodeExample")
        .Input("records: INPUT_TYPE")
        .Attr("names: list(string) >= 1")
        .Output("output: string")
        .Attr("INPUT_TYPE: list({float,double,int32,int64,string})")
        .SetShapeFn([](InferenceContext *c) {
            std::vector<ShapeHandle> input_handles;
            c->input("records", &input_handles);
            if(!input_handles.empty()) {
                for(int i = 0; i < input_handles.size(); i++){
                    ShapeHandle v = input_handles[i];
                    ShapeHandle vv;
                    TF_RETURN_IF_ERROR(c->WithRank(v, 1, &vv));
                }
                c->set_output(0, input_handles[0]);
                return Status::OK();
            } else{
                return errors::Internal("must input tensor to decode");
            }
        });

REGISTER_KERNEL_BUILDER(Name("EncodeExample").Device(DEVICE_CPU), EncodeExampleOp);
