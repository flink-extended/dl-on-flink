package org.flinkextended.flink.ml.util;

import org.junit.Assert;
import org.junit.Test;

public class SysUtilTest {

	@Test
	public void getProjectVersion() {
		Assert.assertEquals("0.4-SNAPSHOT", SysUtil.getProjectVersion());
	}
}