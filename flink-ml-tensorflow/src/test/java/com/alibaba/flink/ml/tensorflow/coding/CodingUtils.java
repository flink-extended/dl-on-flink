package com.alibaba.flink.ml.tensorflow.coding;

import com.alibaba.flink.ml.operator.util.DataTypes;
import com.alibaba.flink.ml.tensorflow.client.TFConfig;
import com.alibaba.flink.ml.tensorflow.util.TFConstants;
import com.alibaba.flink.ml.util.MLConstants;
import org.apache.flink.api.common.typeinfo.BasicArrayTypeInfo;
import org.apache.flink.api.common.typeinfo.BasicTypeInfo;
import org.apache.flink.api.common.typeinfo.TypeInformation;
import org.apache.flink.table.api.TableSchema;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Arrays;

public class CodingUtils {
    private static Logger LOG = LoggerFactory.getLogger(CodingUtils.class);

    /**
     * Map DataTypes list to TypeInformation list
     * @throws RuntimeException when meet unsupported type of DataTypes
     */
    public static TypeInformation[] dataTypesListToTypeInformation(DataTypes[] dataTypes) throws RuntimeException {
        TypeInformation[] ret = new TypeInformation[dataTypes.length];
        for (int i = 0; i < dataTypes.length; i++) {
            ret[i] = dataTypesToTypeInformation(dataTypes[i]);
        }
        return ret;
    }

    /**
     * Map DataTypes class to TypeInformation
     * @throws RuntimeException when meet unsupported type of DataTypes
     */
    public static TypeInformation dataTypesToTypeInformation(DataTypes dataTypes) throws RuntimeException {
        if (dataTypes == DataTypes.STRING) {
            return BasicTypeInfo.STRING_TYPE_INFO;
        } else if (dataTypes == DataTypes.BOOL) {
            return BasicTypeInfo.BOOLEAN_TYPE_INFO;
        } else if (dataTypes == DataTypes.INT_8) {
            return BasicTypeInfo.BYTE_TYPE_INFO;
        } else if (dataTypes == DataTypes.INT_16) {
            return BasicTypeInfo.SHORT_TYPE_INFO;
        } else if (dataTypes == DataTypes.INT_32) {
            return BasicTypeInfo.INT_TYPE_INFO;
        } else if (dataTypes == DataTypes.INT_64) {
            return BasicTypeInfo.LONG_TYPE_INFO;
        } else if (dataTypes == DataTypes.FLOAT_32) {
            return BasicTypeInfo.FLOAT_TYPE_INFO;
        } else if (dataTypes == DataTypes.FLOAT_64) {
            return BasicTypeInfo.DOUBLE_TYPE_INFO;
        } else if (dataTypes == DataTypes.UINT_16) {
            return BasicTypeInfo.CHAR_TYPE_INFO;
        } else if (dataTypes == DataTypes.FLOAT_32_ARRAY) {
            return BasicArrayTypeInfo.FLOAT_ARRAY_TYPE_INFO;
        } else {
            throw new RuntimeException("Unsupported data type of " + dataTypes.toString());
        }
    }

    /**
     * Map TypeInformation list to DataTypes list
     * @throws RuntimeException when meet unsupported type of TypeInformation
     */
    public static DataTypes[] typeInormationListToDataTypes(TypeInformation[] typeInformation) throws RuntimeException {
        DataTypes[] ret = new DataTypes[typeInformation.length];
        for (int i = 0; i < typeInformation.length; i++) {
            ret[i] = typeInformationToDataTypes(typeInformation[i]);
        }
        return ret;
    }

    /**
     * Map TypeInformation class to DataTypes
     * @throws RuntimeException when meet unsupported type of TypeInformation
     */
    public static DataTypes typeInformationToDataTypes(TypeInformation typeInformation) throws RuntimeException {
        if (typeInformation == BasicTypeInfo.STRING_TYPE_INFO) {
            return DataTypes.STRING;
        } else if (typeInformation == BasicTypeInfo.BOOLEAN_TYPE_INFO) {
            return DataTypes.BOOL;
        } else if (typeInformation == BasicTypeInfo.BYTE_TYPE_INFO) {
            return DataTypes.INT_8;
        } else if (typeInformation == BasicTypeInfo.SHORT_TYPE_INFO) {
            return DataTypes.INT_16;
        } else if (typeInformation == BasicTypeInfo.INT_TYPE_INFO) {
            return DataTypes.INT_32;
        } else if (typeInformation == BasicTypeInfo.LONG_TYPE_INFO) {
            return DataTypes.INT_64;
        } else if (typeInformation == BasicTypeInfo.FLOAT_TYPE_INFO) {
            return DataTypes.FLOAT_32;
        } else if (typeInformation == BasicTypeInfo.DOUBLE_TYPE_INFO) {
            return DataTypes.FLOAT_64;
        } else if (typeInformation == BasicTypeInfo.CHAR_TYPE_INFO) {
            return DataTypes.UINT_16;
        } else if (typeInformation == BasicTypeInfo.DATE_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else if (typeInformation == BasicTypeInfo.VOID_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else if (typeInformation == BasicTypeInfo.BIG_INT_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else if (typeInformation == BasicTypeInfo.BIG_DEC_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else if (typeInformation == BasicTypeInfo.INSTANT_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else if (typeInformation == BasicArrayTypeInfo.STRING_ARRAY_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else if (typeInformation == BasicArrayTypeInfo.BOOLEAN_ARRAY_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else if (typeInformation == BasicArrayTypeInfo.BYTE_ARRAY_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else if (typeInformation == BasicArrayTypeInfo.SHORT_ARRAY_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else if (typeInformation == BasicArrayTypeInfo.INT_ARRAY_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else if (typeInformation == BasicArrayTypeInfo.LONG_ARRAY_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else if (typeInformation == BasicArrayTypeInfo.FLOAT_ARRAY_TYPE_INFO) {
            return DataTypes.FLOAT_32_ARRAY;
        } else if (typeInformation == BasicArrayTypeInfo.DOUBLE_ARRAY_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else if (typeInformation == BasicArrayTypeInfo.CHAR_ARRAY_TYPE_INFO) {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        } else {
            throw new RuntimeException("Unsupported data type of " + typeInformation.toString());
        }
    }

    public static void configureEncodeExampleCoding(TFConfig config, String[] encodeNames, DataTypes[] encodeTypes,
                                                    ExampleCodingConfig.ObjectType entryType, Class entryClass) throws RuntimeException {
        String strInput = ExampleCodingConfig.createExampleConfigStr(encodeNames, encodeTypes, entryType, entryClass);
        LOG.info("input tf example config: " + strInput);
        config.getProperties().put(TFConstants.INPUT_TF_EXAMPLE_CONFIG, strInput);
        config.getProperties().put(MLConstants.ENCODING_CLASS, ExampleCoding.class.getCanonicalName());
    }

    public static void configureDecodeExampleCoding(TFConfig config, String[] decodeNames, DataTypes[] decodeTypes,
                                                    ExampleCodingConfig.ObjectType entryType, Class entryClass) throws RuntimeException {
        String strOutput = ExampleCodingConfig.createExampleConfigStr(decodeNames, decodeTypes, entryType, entryClass);
        LOG.info("output tf example config: " + strOutput);
        config.getProperties().put(TFConstants.OUTPUT_TF_EXAMPLE_CONFIG, strOutput);
        config.getProperties().put(MLConstants.DECODING_CLASS, ExampleCoding.class.getCanonicalName());
    }


    public static void configureEncodeExampleCoding(TFConfig config, String[] encodeNames, TypeInformation[] encodeTypes,
                                                    ExampleCodingConfig.ObjectType entryType, Class entryClass) throws RuntimeException {
        DataTypes[] encodeDataTypes = Arrays
                .stream(encodeTypes)
                .map(CodingUtils::typeInformationToDataTypes)
                .toArray(DataTypes[]::new);
        configureEncodeExampleCoding(config, encodeNames, encodeDataTypes, entryType, entryClass);
    }

    public static void configureDecodeExampleCoding(TFConfig config, String[] decodeNames, TypeInformation[] decodeTypes,
                                                    ExampleCodingConfig.ObjectType entryType, Class entryClass) throws RuntimeException {
        DataTypes[] decodeDataTypes = Arrays
                .stream(decodeTypes)
                .map(CodingUtils::typeInformationToDataTypes)
                .toArray(DataTypes[]::new);
        configureDecodeExampleCoding(config, decodeNames, decodeDataTypes, entryType, entryClass);
    }

    public static void configureExampleCoding(TFConfig config, TableSchema encodeSchema, TableSchema decodeSchema,
                                              ExampleCodingConfig.ObjectType entryType, Class entryClass) throws RuntimeException {
        if (encodeSchema != null) {
            configureEncodeExampleCoding(config, encodeSchema.getFieldNames(), encodeSchema.getFieldTypes(),
                    entryType, entryClass);
        }
        if (decodeSchema != null) {
            configureDecodeExampleCoding(config, decodeSchema.getFieldNames(), decodeSchema.getFieldTypes(),
                    entryType, entryClass);
        }
    }
}
