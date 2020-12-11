package com.alibaba.flink.ml.lib.tensorflow.utils;

public class RankUtil {

	public static int[] toRanks(String[] ranks){
		int[] rankArray = new int[ranks.length];
		for(int i = 0; i < ranks.length; i++){
			rankArray[i] = Integer.valueOf(ranks[i]);
		}
		return rankArray;
	}
}
