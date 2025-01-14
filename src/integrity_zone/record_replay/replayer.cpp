#include <replayer.hpp>
#include <request.hpp>
#include <request_types.h>
#include <rr_utils.hpp>
#include <stdafx.hpp>

static uint64_t last_record_timestamp = 0;
static uint64_t last_real_timestamp = 0;
extern bool performance_replay;

int Replayer::replay_request(void* req_buffer)
{
    BaseRequest* req_control = static_cast<BaseRequest*>(req_buffer);
    int reqType = req_control->reqType;
    int op, resp;
    uint64_t record_timestamp;
    uint64_t real_timestamp;
    fread(&op, sizeof(int), 1, replay_file);
    if (op != reqType) {
        print_error("replay fail at %ld, op: %d, reqType: %d, previous_op: %d", ftell(replay_file), op, reqType, previous_op);
        return -RETRY_FAILED;
    }
    if (reqType >= CMD_FLOAT_PLUS && reqType <= CMD_FLOAT_SUM_BULK) {
        EncFloat left, right, res;
        int cmp;
        if (reqType == CMD_FLOAT_CMP) {
            EncFloatCmpRequestData* req = (EncFloatCmpRequestData*)req_buffer;
            char read_buffer[sizeof(int) * 2 + ENC_FLOAT4_LENGTH * 2 + sizeof(uint64_t)];
            char* src = read_buffer;
            fread(read_buffer, sizeof(char), sizeof(int) * 2 + ENC_FLOAT4_LENGTH * 2 + sizeof(uint64_t), replay_file);
            rrprintf(0, src, 5,
                ENC_FLOAT4_LENGTH, &left,
                ENC_FLOAT4_LENGTH, &right,
                sizeof(int), &cmp,
                sizeof(int), &resp,
                sizeof(uint64_t), &record_timestamp);

            if (memcmp(&req->left, &left, ENC_FLOAT4_LENGTH) || memcmp(&req->right, &right, ENC_FLOAT4_LENGTH)) {
                // print_error("float cmp fail at %ld", ftell(read_file_ptr));
                return -RETRY_FAILED;
            }
            req->cmp = cmp;
        } else if (reqType == CMD_FLOAT_SUM_BULK) {
            EncFloatBulkRequestData* req = (EncFloatBulkRequestData*)req_buffer;
            int bulk_size;
            char read_buffer[sizeof(int) * 2 + ENC_FLOAT4_LENGTH + sizeof(uint64_t)];
            char* src = read_buffer;
            fread(read_buffer, sizeof(char), sizeof(int) * 2 + ENC_FLOAT4_LENGTH + sizeof(uint64_t), replay_file);
            rrprintf(0, src, 4,
                sizeof(int), &bulk_size,
                ENC_FLOAT4_LENGTH, &res,
                sizeof(int), &resp,
                sizeof(uint64_t), &record_timestamp);

            if (bulk_size != req->bulk_size) {
                // print_error("float sum fail at %ld, req->bulk_size: %d, bulk_size:%d", ftell(read_file_ptr), req->bulk_size, bulk_size);
                return -RETRY_FAILED;
            }

            char read_buffer_operators[bulk_size * ENC_FLOAT4_LENGTH];
            EncFloat operand;
            src = read_buffer_operators;
            fread(read_buffer_operators, sizeof(char), bulk_size * ENC_FLOAT4_LENGTH, replay_file);
            for (int i = 0; i < bulk_size; i++) {
                memcpy(&operand, src, ENC_FLOAT4_LENGTH);
                if (memcmp(&operand, &req->items[i], ENC_FLOAT4_LENGTH)) {
                    // print_error("float sum operands %d different", i);
                    return -RETRY_FAILED;
                }
                src += ENC_FLOAT4_LENGTH;
            }

            memcpy(&req->res, &res, ENC_FLOAT4_LENGTH);
        } else {
            EncFloatCalcRequestData* req = (EncFloatCalcRequestData*)req_buffer;
            char read_buffer[sizeof(int) + ENC_FLOAT4_LENGTH * 3 + sizeof(uint64_t)];
            char* src = read_buffer;
            fread(read_buffer, sizeof(char), sizeof(int) + ENC_FLOAT4_LENGTH * 3 + sizeof(uint64_t), replay_file);
            rrprintf(0, src, 5,
                ENC_FLOAT4_LENGTH, &left,
                ENC_FLOAT4_LENGTH, &right,
                ENC_FLOAT4_LENGTH, &res,
                sizeof(int), &resp,
                sizeof(uint64_t), &record_timestamp);

            if (memcmp(&left, &req->left, ENC_FLOAT4_LENGTH) || memcmp(&right, &req->right, ENC_FLOAT4_LENGTH)) {
                // print_error("float ops fail at %ld", ftell(read_file_ptr));
                return -RETRY_FAILED;
            }

            memcpy(&req->res, &res, ENC_FLOAT4_LENGTH);
        }
    } else if (reqType >= CMD_INT_PLUS && reqType <= CMD_INT_SUM_BULK) {
        EncInt left, right, res;
        int cmp;
        if (reqType == CMD_INT_CMP) {
            EncIntCmpRequestData* req = (EncIntCmpRequestData*)req_buffer;
            char read_buffer[sizeof(int) * 2 + ENC_INT32_LENGTH * 2 + sizeof(uint64_t)];
            char* src = read_buffer;
            fread(read_buffer, sizeof(char), sizeof(int) * 2 + ENC_INT32_LENGTH * 2 + sizeof(uint64_t), replay_file);
            rrprintf(0, src, 5,
                ENC_INT32_LENGTH, &left,
                ENC_INT32_LENGTH, &right,
                sizeof(int), &cmp,
                sizeof(int), &resp,
                sizeof(uint64_t), &record_timestamp);

            if (memcmp(&left, &req->left, ENC_INT32_LENGTH) || memcmp(&right, &req->right, ENC_INT32_LENGTH)) {
                // print_error("int cmp fail at %ld", ftell(read_file_ptr));
                return -RETRY_FAILED;
            }

            req->cmp = cmp;
        } else if (reqType == CMD_INT_SUM_BULK) {
            EncIntBulkRequestData* req = (EncIntBulkRequestData*)req_buffer;
            int bulk_size;
            char read_buffer[sizeof(int) * 2 + ENC_INT32_LENGTH + sizeof(uint64_t)];
            char* src = read_buffer;
            fread(read_buffer, sizeof(char), sizeof(int) * 2 + ENC_INT32_LENGTH + sizeof(uint64_t), replay_file);
            rrprintf(0, src, 4,
                sizeof(int), &bulk_size,
                ENC_INT32_LENGTH, &res,
                sizeof(int), &resp,
                sizeof(uint64_t), &record_timestamp);

            if (bulk_size != req->bulk_size) {
                // print_error("int sum fail at %ld, req->bulk_size: %d, bulk_size:%d", ftell(read_file_ptr), req->bulk_size, bulk_size);
                return -RETRY_FAILED;
            }

            char read_buffer_operators[bulk_size * ENC_INT32_LENGTH];
            EncFloat operand;
            src = read_buffer_operators;
            fread(read_buffer_operators, sizeof(char), bulk_size * ENC_INT32_LENGTH, replay_file);
            for (int i = 0; i < bulk_size; i++) {
                memcpy(&operand, src, ENC_INT32_LENGTH);
                if (memcmp(&operand, &req->items[i], ENC_INT32_LENGTH)) {
                    // print_error("int sum operands %d different", i);
                    return -RETRY_FAILED;
                }
                src += ENC_INT32_LENGTH;
            }

            memcpy(&req->res, &res, ENC_INT32_LENGTH);
        } else {
            EncIntCalcRequestData* req = (EncIntCalcRequestData*)req_buffer;
            char read_buffer[sizeof(int) + ENC_INT32_LENGTH * 3 + sizeof(uint64_t)];
            char* src = read_buffer;
            fread(read_buffer, sizeof(char), sizeof(int) + ENC_INT32_LENGTH * 3 + sizeof(uint64_t), replay_file);
            rrprintf(0, src, 5,
                ENC_INT32_LENGTH, &left,
                ENC_INT32_LENGTH, &right,
                ENC_INT32_LENGTH, &res,
                sizeof(int), &resp,
                sizeof(uint64_t), &record_timestamp);

            if (memcmp(&left, &req->left, ENC_INT32_LENGTH) || memcmp(&right, &req->right, ENC_INT32_LENGTH)) {
                // print_error("int ops fail at %ld", ftell(read_file_ptr));
                return -RETRY_FAILED;
            }

            memcpy(&req->res, &res, ENC_INT32_LENGTH);
        }
    } else if (reqType >= CMD_STRING_CMP && reqType <= CMD_STRING_LIKE) {
        EncStr left, right, res;
        int cmp;
        if (reqType == CMD_STRING_CMP || reqType == CMD_STRING_LIKE) {
            EncStrCmpRequestData* req = (EncStrCmpRequestData*)req_buffer;
            int left_length, right_length;
            fread(&left_length, sizeof(int), 1, replay_file);
            fread(&right_length, sizeof(int), 1, replay_file);

            if (left_length != encstr_size(req->left) || right_length != encstr_size(req->right)) {
                // print_error("string cmp fail at %ld, length not right", ftell(read_file_ptr));
                return -RETRY_FAILED;
            }

            char read_buffer[left_length + right_length + sizeof(int) * 2 + sizeof(uint64_t)];
            char* src = read_buffer;
            fread(read_buffer, sizeof(char), left_length + right_length + sizeof(int) * 2 + sizeof(uint64_t), replay_file);
            rrprintf(0, src, 5,
                left_length, &left,
                right_length, &right,
                sizeof(int), &cmp,
                sizeof(int), &resp,
                sizeof(uint64_t), &record_timestamp);

            req->cmp = cmp;
        } else if (req_control->reqType == CMD_STRING_SUBSTRING) {
            SubstringRequestData* req = (SubstringRequestData*)req_buffer;
            EncStr str;
            EncInt start, length;
            int str_length, result_length;
            fread(&str_length, sizeof(int), 1, replay_file);
            fread(&result_length, sizeof(int), 1, replay_file);

            if (str_length != encstr_size(req->str)) {
                // print_error("string substring fail at %ld, length not right", ftell(read_file_ptr));
                return -RETRY_FAILED;
            }

            char read_buffer[str_length + result_length + sizeof(int) + ENC_INT32_LENGTH * 2 + sizeof(uint64_t)];
            char* src = read_buffer;
            fread(read_buffer, sizeof(char), str_length + result_length + sizeof(int) + ENC_INT32_LENGTH * 2 + sizeof(uint64_t), replay_file);
            rrprintf(0, src, 6,
                str_length, &str,
                ENC_INT32_LENGTH, &start,
                ENC_INT32_LENGTH, &length,
                result_length, &res,
                sizeof(int), &resp,
                sizeof(uint64_t), &record_timestamp);

            if (memcmp(&str, &req->str, str_length) || memcmp(&start, &req->start, ENC_INT32_LENGTH) || memcmp(&length, &req->length, ENC_INT32_LENGTH)) {
                // print_error("string substring fail at %ld, contents mismatch", ftell(read_file_ptr));
                return -RETRY_FAILED;
            }
            memcpy(&req->res, &res, result_length);
        } else {
            EncStrCalcRequestData* req = (EncStrCalcRequestData*)req_buffer;
            int left_length, right_length, res_length;
            fread(&left_length, sizeof(int), 1, replay_file);
            fread(&right_length, sizeof(int), 1, replay_file);
            fread(&res_length, sizeof(int), 1, replay_file);

            if (left_length != encstr_size(req->left) || right_length != encstr_size(req->right)) {
                // print_error("string ops fail at %ld, length not right", ftell(read_file_ptr));
                return -RETRY_FAILED;
            }

            char read_buffer[sizeof(int) + left_length + right_length + res_length + sizeof(uint64_t)];
            fread(read_buffer, sizeof(char), sizeof(int) + left_length + right_length + res_length + sizeof(uint64_t), replay_file);
            char* src = read_buffer;
            rrprintf(0, src, 5,
                left_length, &left,
                right_length, &right,
                res_length, &res,
                sizeof(int), &resp,
                sizeof(uint64_t), &record_timestamp);

            if (memcmp(&left, &req->left, left_length) || memcmp(&right, &req->right, right_length)) {
                // print_error("string ops fail at %ld, contents mismatch", ftell(read_file_ptr));
                return -RETRY_FAILED;
            }
            memcpy(&req->res, &res, res_length);
        }
    } else if (reqType >= CMD_TIMESTAMP_CMP && reqType <= CMD_TIMESTAMP_EXTRACT_YEAR) {
        if (req_control->reqType == CMD_TIMESTAMP_CMP) {
            int cmp;
            EncTimestamp left, right;
            EncTimestampCmpRequestData* req = (EncTimestampCmpRequestData*)req_buffer;
            char read_buffer[sizeof(int) * 2 + ENC_TIMESTAMP_LENGTH * 2 + sizeof(uint64_t)];
            fread(read_buffer, sizeof(char), sizeof(int) * 2 + ENC_TIMESTAMP_LENGTH * 2 + sizeof(uint64_t), replay_file);
            char* src = read_buffer;
            rrprintf(0, src, 5,
                ENC_TIMESTAMP_LENGTH, &left,
                ENC_TIMESTAMP_LENGTH, &right,
                sizeof(int), &cmp,
                sizeof(int), &resp,
                sizeof(uint64_t), &record_timestamp);

            if (memcmp(&left, &req->left, ENC_TIMESTAMP_LENGTH) || memcmp(&right, &req->right, ENC_TIMESTAMP_LENGTH)) {
                // print_info("timestamp cmp fail at %ld", ftell(read_file_ptr));
                return -RETRY_FAILED;
            }
            req->cmp = cmp;
        } else if (req_control->reqType == CMD_TIMESTAMP_EXTRACT_YEAR) {
            EncTimestamp in;
            EncInt out;
            EncTimestampExtractYearRequestData* req = (EncTimestampExtractYearRequestData*)req_buffer;
            char read_buffer[sizeof(int) + ENC_TIMESTAMP_LENGTH + ENC_INT32_LENGTH + sizeof(uint64_t)];
            fread(read_buffer, sizeof(char), sizeof(int) + ENC_TIMESTAMP_LENGTH + ENC_INT32_LENGTH + sizeof(uint64_t), replay_file);
            char* src = read_buffer;
            rrprintf(0, src, 4,
                ENC_TIMESTAMP_LENGTH, &in,
                ENC_INT32_LENGTH, &out,
                sizeof(int), &resp,
                sizeof(uint64_t), &record_timestamp);

            if (memcmp(&in, &req->in, ENC_TIMESTAMP_LENGTH)) {
                // print_info("timestamp extract fail at %ld", ftell(read_file_ptr));
                return -RETRY_FAILED;
            }
            memcpy(&req->res, &out, ENC_INT32_LENGTH);
        }
    }
    previous_op = op;

    if (performance_replay) {
        real_timestamp = get_timestamp();
        if (last_real_timestamp && last_record_timestamp) {
            uint64_t end_timestamp = last_real_timestamp + record_timestamp - last_record_timestamp;
            do {
                real_timestamp = get_timestamp();
            } while (real_timestamp < end_timestamp);
        }
        last_real_timestamp = real_timestamp;
        last_record_timestamp = record_timestamp;
    }

    return resp;
}

void Replayer::update_replay_files(const std::vector<std::string>& fileList)
{
    filenames = fileList;
    replay_file = nullptr;
}

int Replayer::replay(void* request_buffer)
{
    int reqType = static_cast<BaseRequest*>(request_buffer)->reqType;
    if (reqType == CMD_FLOAT_ENC
        || reqType == CMD_FLOAT_DEC
        || reqType == CMD_INT_ENC
        || reqType == CMD_INT_DEC
        || reqType == CMD_STRING_ENC
        || reqType == CMD_STRING_DEC
        || reqType == CMD_TIMESTAMP_ENC
        || reqType == CMD_TIMESTAMP_DEC) {
        return NOT_REPLAY;
    }
    if (replay_file == nullptr) {
        /* initilize replay_file by iterating through records, and find one that match the first */
        for (auto filename : filenames) {
            replay_file = fopen(filename.c_str(), "r+b");
            int ret = replay_request(request_buffer);
            if (ret == -RETRY_FAILED) {
                fclose(replay_file);
                replay_file = nullptr;
            } else {
                return ret;
            }
        }
        return -1; // not valid record file found. error.
    }
    return replay_request(request_buffer);
}
