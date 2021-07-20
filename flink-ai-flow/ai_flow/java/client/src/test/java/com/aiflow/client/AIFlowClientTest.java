/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

package com.aiflow.client;

import com.aiflow.common.DataType;
import com.aiflow.common.ModelStage;
import com.aiflow.common.Status;
import com.aiflow.entity.ArtifactMeta;
import com.aiflow.entity.DatasetMeta;
import com.aiflow.entity.ModelMeta;
import com.aiflow.entity.ModelRelationMeta;
import com.aiflow.entity.ModelVersion;
import com.aiflow.entity.ModelVersionMeta;
import com.aiflow.entity.ModelVersionRelationMeta;
import com.aiflow.entity.ProjectMeta;
import com.aiflow.entity.RegisteredModel;
import com.aiflow.entity.WorkflowMeta;
import com.aiflow.exception.AIFlowException;
import com.aiflow.notification.client.EventWatcher;
import com.aiflow.notification.entity.EventMeta;
import com.aiflow.proto.Message;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.io.InputStream;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;

public class AIFlowClientTest {

    private static final String LOCALHOST = "localhost";
    private static final int SEC = 1000;

    private static AIFlowClient client;
    private static final Map EMPTY_MAP = Collections.emptyMap();

    @BeforeAll
    public static void beforeClass() throws Exception {
        int port = Integer.valueOf(getProperties("port"));
        client = new AIFlowClient(LOCALHOST + ":" + port, "default",
                false, 1 * SEC, 1 * SEC, 1 * SEC);
    }

    @AfterAll
    public static void afterClass() throws Exception {
        client.stopListenEvent("default", "");
    }



    private static String getProperties(String key) throws IOException {
        InputStream in = new Object() {
            public InputStream getInputStream() {
                return this.getClass().getClassLoader().getResourceAsStream("test.properties");
            }
        }.getInputStream();
        Properties properties = new Properties();
        properties.load(in);
        return properties.getProperty(key);
    }

    public static void main(String[] args) throws IOException {
        System.out.println(getProperties("port"));
    }

    // test dataset

    @Test
    public void testRegisterDataset() throws Exception {
        String datasetName = "dataset_name";
        client.registerDataset(datasetName, "csv", "good dataset", "mysql://",
                new HashMap<String, String>() {{
                    put("key1", "value1");
                    put("key2", "value2");
                }},
                Arrays.asList("col1", "col2"),
                Arrays.asList(DataType.STRING, DataType.STRING));
        DatasetMeta notExistsDataset = client.getDatasetById(2L);
        Assertions.assertNull(notExistsDataset);

        DatasetMeta datasetById = client.getDatasetById(1L);
        Assertions.assertEquals(datasetName, datasetById.getName());

        DatasetMeta datasetByName = client.getDatasetByName(datasetName);
        Assertions.assertEquals(1L, datasetByName.getUuid().longValue());

        client.deleteDatasetByName(datasetName);
    }

    @Test
    public void testRegisterDatasetWithCatalog() throws Exception {
        String datasetName = "dataset_name";
        String catalogName = "hive_catalog";
        client.registerDatasetWithCatalog(datasetName, catalogName, "hive", "/path/to/conf", "my_db",  "my_table");
        DatasetMeta datasetById = client.getDatasetById(1L);
        Assertions.assertEquals(datasetName, datasetById.getName());
        Assertions.assertEquals(catalogName, datasetById.getCatalogName());

        DatasetMeta datasetByName = client.getDatasetByName(datasetName);
        Assertions.assertEquals(1L, datasetByName.getUuid().longValue());
        Assertions.assertEquals(catalogName, datasetByName.getCatalogName());
    }

    @Test
    public void testDoubleRegisterDataset() throws Exception {
        String datasetName = "dataset_name";
        DatasetMeta dataset1 = client.registerDataset(datasetName, "csv", "good dataset", "mysql://",
                new HashMap<String, String>() {{
                    put("key1", "value1");
                    put("key2", "value2");
                }},
                Arrays.asList("col1", "col2"),
                Arrays.asList(DataType.STRING, DataType.STRING));
        DatasetMeta dataset2 = client.registerDataset(datasetName, "csv", "good dataset", "mysql://",
                new HashMap<String, String>() {{
                    put("key1", "value1");
                    put("key2", "value2");
                }},
                Arrays.asList("col1", "col2"),
                Arrays.asList(DataType.STRING, DataType.STRING));
        Assertions.assertEquals(dataset1.getUuid(), dataset2.getUuid());
        Assertions.assertThrows(AIFlowException.class, () -> client.registerDataset(
                datasetName, "txt", "good dataset", "mysql://",
                new HashMap<String, String>() {{
                    put("key1", "value1");
                    put("key2", "value2");
                }},
                Arrays.asList("col1", "col2"),
                Arrays.asList(DataType.STRING, DataType.STRING)));
    }

    @Test
    public void testListDataset() throws Exception {
        String datasetName1 = "dataset_name_1";
        String datasetName2 = "dataset_name_2";
        client.registerDataset(datasetName1, "csv", "good dataset", "mysql://",
                new HashMap<String, String>() {{
                    put("key1", "value1");
                    put("key2", "value2");
                }},
                Arrays.asList("col1", "col2"),
                Arrays.asList(DataType.STRING, DataType.STRING));
        client.registerDataset(datasetName2, "csv", "good dataset", "mysql://",
                new HashMap<String, String>() {{
                    put("key1", "value1");
                    put("key2", "value2");
                }},
                Arrays.asList("col1", "col2"),
                Arrays.asList(DataType.STRING, DataType.STRING));
        List<DatasetMeta> datasets = client.listDatasets(5L, 0L);
        Assertions.assertEquals(2, datasets.size());
        Assertions.assertEquals(datasetName1, datasets.get(0).getName());
        Assertions.assertEquals(datasetName2, datasets.get(1).getName());
    }

    @Test
    public void testSaveAndListDatasets() throws Exception {
        String datasetName1 = "dataset_name_1";
        String datasetName2 = "dataset_name_2";
        DatasetMeta dataset1 = new DatasetMeta();
        dataset1.setName(datasetName1);
        dataset1.setProperties(EMPTY_MAP);
        DatasetMeta dataset2 = new DatasetMeta();
        dataset2.setName(datasetName2);
        dataset2.setProperties(EMPTY_MAP);
        List<DatasetMeta> response = client.registerDatasets(Arrays.asList(dataset1, dataset2));
        Assertions.assertEquals(2, response.size());
        Assertions.assertEquals(datasetName1, response.get(0).getName());
        Assertions.assertEquals(datasetName2, response.get(1).getName());

        List<DatasetMeta> datasetList = client.listDatasets(5L, 0L);
        Assertions.assertEquals(2, datasetList.size());
        Assertions.assertEquals(datasetName1, datasetList.get(0).getName());
        Assertions.assertEquals(datasetName2, datasetList.get(1).getName());
    }

    @Test
    public void testDeleteDataset() throws Exception {
        String datasetName1 = "dataset_name_1";
        client.registerDataset(datasetName1, "csv", "good dataset", "mysql://",
                new HashMap<String, String>() {{
                    put("key1", "value1");
                    put("key2", "value2");
                }},
                Arrays.asList("col1", "col2"),
                Arrays.asList(DataType.STRING, DataType.STRING));
        Assertions.assertEquals(Status.OK, client.deleteDatasetByName(datasetName1));
        Assertions.assertNull(client.getDatasetByName(datasetName1));
        Assertions.assertNull(client.listDatasets(5L, 0L));
    }

    @Test
    public void testUpdateDataset() throws Exception {
        String datasetName1 = "dataset_name_1";
        client.registerDataset(datasetName1, "csv", "good dataset", "mysql://",
                new HashMap<String, String>() {{
                    put("key1", "value1");
                    put("key2", "value2");
                }},
                Arrays.asList("col1", "col2"),
                Arrays.asList(DataType.STRING, DataType.STRING));
        long now = System.currentTimeMillis();
        client.updateDataset(datasetName1, "npz", "", "",
                new HashMap<String, String>() {{
                    put("key3", "value3");
                    put("key4", "value4");
                }},
                Arrays.asList("col1", "col2"),
                Arrays.asList(DataType.STRING, DataType.STRING),
                "", "hive", "", "", "");
        DatasetMeta dataset = client.getDatasetByName(datasetName1);
        Assertions.assertEquals("npz", dataset.getDataFormat());
        Assertions.assertEquals("hive", dataset.getCatalogType());
        System.out.println(dataset.getUpdateTime());
        System.out.println(now);
        Assertions.assertTrue(dataset.getUpdateTime() > now);
    }

    // test project

    @Test
    public void testRegisterProject() throws Exception {
        String projectName = "project_name";
        String uri = "www.code.com";
        ProjectMeta response = client.registerProject(projectName, uri, EMPTY_MAP);
        long projectId = response.getUuid();
        ProjectMeta projectById = client.getProjectById(projectId);
        Assertions.assertEquals(uri, projectById.getUri());
        ProjectMeta projectByName = client.getProjectByName(projectName);
        Assertions.assertEquals(uri, projectByName.getUri());
    }

    @Test
    public void testDoubleRegisterProject() throws Exception {
        String projectName = "project_name";
        String uri = "www.code.com";
        client.registerProject(projectName, uri, EMPTY_MAP);
        client.registerProject(projectName, uri, EMPTY_MAP);
        Assertions.assertThrows(AIFlowException.class, () -> client.registerProject(projectName, uri+ "_new", EMPTY_MAP));
    }

    @Test
    public void testListProjects() throws Exception {
        String projectName1 = "project_name_1";
        String uri = "www.code.com";
        String projectName2 = "project_name_2";
        client.registerProject(projectName1, uri, EMPTY_MAP);
        client.registerProject(projectName2, uri, EMPTY_MAP);
        List<ProjectMeta> projects = client.listProject(5L, 0L);
        Assertions.assertEquals(2, projects.size());
    }

    @Test
    public void testDeleteProject() throws Exception {
        String projectName1 = "project_name_1";
        String uri = "www.code.com";
        String projectName2 = "project_name_2";
        ProjectMeta response1 = client.registerProject(projectName1, uri, EMPTY_MAP);
        ProjectMeta response2 = client.registerProject(projectName2, uri, EMPTY_MAP);
        Assertions.assertNotNull(client.getProjectById(response1.getUuid()));
        Assertions.assertNotNull(client.getProjectById(response2.getUuid()));

        client.deleteProjectByName(response1.getName());
        Assertions.assertNull(client.getProjectById(response1.getUuid()));

        client.deleteProjectById(response2.getUuid());
        Assertions.assertNull(client.getProjectById(response2.getUuid()));
    }

    @Test
    public void testUpdateProject() throws Exception {
        String projectName = "project_name";
        String uri = "www.code.com";
        String newUri = "www.new_code.com";
        client.registerProject(projectName, uri, EMPTY_MAP);
        Assertions.assertEquals(uri, client.getProjectByName(projectName).getUri());
        client.updateProject(projectName, newUri, EMPTY_MAP);
        Assertions.assertEquals(newUri, client.getProjectByName(projectName).getUri());
    }

    // test workflow

    @Test
    public void testRegisterWorkflow() throws Exception {
        String projectName = "project_name";
        String workflowName = "workflow_name";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);
        WorkflowMeta response = client.registerWorkflow(workflowName, project.getUuid(), new HashMap<String, String>() {{
            put("key1", "value1");
            put("key2", "value2");
        }});
        Assertions.assertEquals(workflowName, response.getName());

        Assertions.assertEquals("value1", client.getWorkflowById(response.getUuid()).getProperties().get("key1"));
        Assertions.assertEquals("value1", client.getWorkflowByName(projectName, workflowName).getProperties().get("key1"));
    }

    @Test
    public void testDoubleRegisterWorkflow() throws Exception {
        String projectName = "project_name";
        String workflowName = "workflow_name";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);
        WorkflowMeta response = client.registerWorkflow(workflowName, project.getUuid(), EMPTY_MAP);
        Assertions.assertThrows(AIFlowException.class, () -> client.registerWorkflow(
                workflowName, project.getUuid(), EMPTY_MAP));
    }

    @Test
    public void testListWorkflows() throws Exception {
        String projectName = "project_name";
        String workflowName1 = "workflow_name_1";
        String workflowName2 = "workflow_name_2";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);
        client.registerWorkflow(workflowName1, project.getUuid(), EMPTY_MAP);
        client.registerWorkflow(workflowName2, project.getUuid(), EMPTY_MAP);
        Assertions.assertEquals(2, client.listWorkflows(projectName, 5L, 0L).size());
    }

    @Test
    public void testDeleteWorkflow() throws Exception {
        String projectName = "project_name";
        String workflowName1 = "workflow_name_1";
        String workflowName2 = "workflow_name_2";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);
        WorkflowMeta response1 = client.registerWorkflow(workflowName1, project.getUuid(), EMPTY_MAP);
        WorkflowMeta response2 = client.registerWorkflow(workflowName2, project.getUuid(), EMPTY_MAP);

        Assertions.assertNotNull(client.getWorkflowById(response1.getUuid()));
        client.deleteWorkflowById(response1.getUuid());
        Assertions.assertNull(client.getWorkflowById(response1.getUuid()));

        Assertions.assertNotNull(client.getWorkflowById(response2.getUuid()));
        client.deleteWorkflowByName(projectName, workflowName2);
        Assertions.assertNull(client.getWorkflowById(response2.getUuid()));
    }

    @Test
    public void testUpdateWorkflow() throws Exception {
        String projectName = "project_name";
        String workflowName = "workflow_name";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);
        WorkflowMeta response = client.registerWorkflow(workflowName, project.getUuid(), new HashMap<String, String>() {{
            put("key1", "value1");
        }});
        Assertions.assertEquals("value1", client.getWorkflowById(response.getUuid()).getProperties().get("key1"));
        client.updateWorkflow(workflowName, projectName, new HashMap<String, String>() {{
            put("key1", "value2");
        }});
        Assertions.assertEquals("value2", client.getWorkflowById(response.getUuid()).getProperties().get("key1"));
    }

    // test model

    @Test
    public void testModelOperations() throws Exception {
        String projectName = "project_name";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);

        String modelName = "model_name";
        String modelDesc = "model_description";
        ModelMeta model = client.registerModel(modelName, modelDesc, project.getUuid());

        Assertions.assertEquals(modelDesc, client.getModelById(model.getUuid()).getModelDesc());
        Assertions.assertEquals(modelDesc, client.getModelByName(modelName).getModelDesc());

        String modelName2 = "model_name_2";
        String modelDesc2 = "model_description_2";
        client.registerModel(modelName2, modelDesc2, project.getUuid());

        Assertions.assertEquals(2, client.listRegisteredModels().size());
    }

    @Test
    public void testRegisterModelRelation() throws Exception {
        String projectName = "project_name";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);

        String modelName = "model_name";
        ModelRelationMeta response = client.registerModelRelation(modelName, project.getUuid());
        Assertions.assertEquals(modelName, client.getModelRelationById(response.getUuid()).getName());
        Assertions.assertEquals(project.getUuid(), client.getModelRelationByName(modelName).getProjectId());
    }

    @Test
    public void testListModelRelation() throws Exception {
        String projectName = "project_name";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);

        String modelName1 = "model_name_1";
        String modelName2 = "model_name_2";
        client.registerModelRelation(modelName1, project.getUuid());
        client.registerModelRelation(modelName2, project.getUuid());

        List<ModelRelationMeta> modelRelationList = client.listModelRelation(5L, 0L);
        Assertions.assertEquals(2, modelRelationList.size());
        Assertions.assertEquals(modelName1, modelRelationList.get(0).getName());
        Assertions.assertEquals(modelName2, modelRelationList.get(1).getName());
    }

    @Test
    public void deleteModelRelation() throws Exception {
        String projectName = "project_name";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);

        String modelName1 = "model_name_1";
        String modelName2 = "model_name_2";
        ModelRelationMeta response1 = client.registerModelRelation(modelName1, project.getUuid());
        ModelRelationMeta response2 = client.registerModelRelation(modelName2, project.getUuid());
        Assertions.assertNotNull(client.getModelRelationByName(modelName1));
        Assertions.assertNotNull(client.getModelRelationByName(modelName2));

        client.deleteModelRelationById(response1.getUuid());
        Assertions.assertNull(client.getModelRelationByName(modelName1));
        client.deleteModelRelationByName(modelName2);
        Assertions.assertNull(client.getModelRelationByName(modelName2));
    }

    // test model version

    @Test
    public void testModelVersionOperations() throws Exception {
        String projectName = "project_name";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);
        String modelName = "model_name";
        String modelDesc = "model_description";
        ModelMeta model = client.registerModel(modelName, modelDesc, project.getUuid());

        Assertions.assertNull(client.getModelVersionByVersion("1", model.getUuid()));
        String modelPath = "fs://source1.pkl";
        String modelType = "model_type";
        String versionDesc = "this is a good version";
        ModelVersionMeta response = client.registerModelVersion(modelPath, modelType, versionDesc, model.getUuid(), Message.ModelVersionStage.GENERATED, null);
        Assertions.assertEquals("1", response.getVersion());

        ModelVersionMeta modelVersion = client.getModelVersionByVersion(response.getVersion(), model.getUuid());
        Assertions.assertEquals("fs://source1.pkl", modelVersion.getModelPath());

        ModelVersion update_response = client.updateModelVersion(modelName, modelVersion.getVersion(),
                modelPath + "_new", modelType + "_new", versionDesc + "_new", ModelStage.DEPLOYED);
        Assertions.assertEquals(ModelStage.DEPLOYED, update_response.getCurrentStage());

        String modelPath2 = "fs://source2.pkl";
        String modelType2 = "model_type_2";
        String versionDesc2 = "this is a good version 2";
        ModelVersionMeta response2 = client.registerModelVersion(modelPath2, modelType2, versionDesc2, model.getUuid(), Message.ModelVersionStage.GENERATED,null);
        Assertions.assertEquals("2", response2.getVersion());

        List<ModelVersionRelationMeta> modelVersionRelationList = client.listModelVersionRelation(model.getUuid(), 5L, 0L);
        Assertions.assertEquals(2, modelVersionRelationList.size());

        client.deleteModelVersionByVersion("2", model.getUuid());
        List<ModelVersionRelationMeta> modelVersionRelationList2 = client.listModelVersionRelation(model.getUuid(), 5L, 0L);
        Assertions.assertEquals(1, modelVersionRelationList2.size());

        ModelVersionMeta response3 = client.registerModelVersion(modelPath2, modelType2, versionDesc2, model.getUuid(), Message.ModelVersionStage.GENERATED,null);
        Assertions.assertEquals("2", response3.getVersion());
    }

    @Test
    public void testListModelVersion() throws Exception {
        String projectName = "project_name";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);

        String modelName = "model";
        ModelRelationMeta model = client.registerModelRelation(modelName, project.getUuid());
        client.registerModelVersionRelation("1", model.getUuid(), null);
        client.registerModelVersionRelation("2", model.getUuid(), null);
        Assertions.assertEquals(2, client.listModelVersionRelation(model.getUuid(), 5L, 0L).size());
    }

    @Test
    public void testDeleteModelVersionByVersion() throws Exception {
        String projectName = "project_name";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);

        String modelName = "model";
        ModelRelationMeta model = client.registerModelRelation(modelName, project.getUuid());
        client.registerModelVersionRelation("1", model.getUuid(), null);
        Assertions.assertNotNull(client.getModelVersionRelationByVersion("1", model.getUuid()));
        client.deleteModelVersionByVersion("1", model.getUuid());
        Assertions.assertNull(client.getModelVersionRelationByVersion("1", model.getUuid()));
    }

    // test artifact

    @Test
    public void testRegisterArtifact() throws Exception {
        String artifactName = "artifact_name";
        String artifactType = "artifact_type";
        String description = "description";
        String uri = "file:///artifact";
        ArtifactMeta artifact = client.registerArtifact(artifactName, artifactType, description, uri, EMPTY_MAP);
        Assertions.assertEquals(artifactType, client.getArtifactById(artifact.getUuid()).getArtifactType());
        Assertions.assertEquals(artifactType, client.getArtifactByName(artifactName).getArtifactType());
    }

    @Test
    public void testDoubleRegisterArtifact() throws Exception {
        String artifactName = "artifact_name";
        String artifactType = "artifact_type";
        String description = "description";
        String uri = "file:///artifact";
        ArtifactMeta artifact1 = client.registerArtifact(artifactName, artifactType, description, uri, EMPTY_MAP);
        ArtifactMeta artifact2 = client.registerArtifact(artifactName, artifactType, description, uri, EMPTY_MAP);
        Assertions.assertEquals(artifact1.getDescription(), artifact2.getDescription());
        Assertions.assertThrows(AIFlowException.class, () -> client.registerArtifact(
                artifactName, artifactType, description, uri + "_new", EMPTY_MAP));
    }

    @Test
    public void testListArtifacts() throws Exception {
        String artifactName = "artifact_name";
        String artifactType = "artifact_type";
        String description = "description";
        String uri = "file:///artifact";
        client.registerArtifact(artifactName, artifactType, description, uri, EMPTY_MAP);
        client.registerArtifact(artifactName + "_new", artifactType, description, uri, EMPTY_MAP);
        Assertions.assertEquals(2, client.listArtifact(5L, 0L).size());
    }

    @Test
    public void testDeleteArtifact() throws Exception {
        String artifactName = "artifact_name";
        String artifactType = "artifact_type";
        String description = "description";
        String uri = "file:///artifact";
        client.registerArtifact(artifactName, artifactType, description, uri, EMPTY_MAP);
        ArtifactMeta response = client.registerArtifact(artifactName + "_new", artifactType, description, uri, EMPTY_MAP);
        Assertions.assertNotNull(client.getArtifactById(response.getUuid()));
        Assertions.assertNotNull(client.getArtifactByName(artifactName));

        client.deleteArtifactById(response.getUuid());
        Assertions.assertNull(client.getArtifactById(response.getUuid()));
        client.deleteArtifactByName(artifactName);
        Assertions.assertNull(client.getArtifactByName(artifactName));
    }

    @Test
    public void testUpdateArtifact() throws Exception {
        String artifactName = "artifact_name";
        String artifactType = "artifact_type";
        String description = "description";
        String uri = "file:///artifact";
        ArtifactMeta response = client.registerArtifact(artifactName, artifactType, description, uri, EMPTY_MAP);

        Assertions.assertEquals(description, client.getArtifactById(response.getUuid()).getDescription());
        client.updateArtifact(artifactName, artifactType, description + "_new", uri, EMPTY_MAP);
        Assertions.assertEquals(description + "_new", client.getArtifactById(response.getUuid()).getDescription());
    }

    // test model center

    @Test
    public void testDoubleCreateRegisteredModel() throws Exception {
        String modelName = "test_create_registered_model";
        String modelDesc = "test_create_registered_model_desc";
        RegisteredModel response = client.createRegisteredModel(modelName, modelDesc);
        Assertions.assertEquals(modelDesc, response.getModelDesc());
        // It's not allowed to create a registered model with the same name but different fields.
        client.createRegisteredModel(modelName, modelDesc);
        Assertions.assertThrows(AIFlowException.class, () ->  client.createRegisteredModel(modelName, ""));

        String projectName = "project_name";
        String uri = "www.code.com";
        ProjectMeta project = client.registerProject(projectName, uri, EMPTY_MAP);
        client.registerModel(modelName, modelDesc, project.getUuid());
        client.registerModel(modelName, modelDesc, project.getUuid());
        Assertions.assertThrows(AIFlowException.class, () -> client.registerModel(modelName, "", project.getUuid()));
    }

    @Test
    public void testDeleteRegisteredModel() throws Exception {
        String modelName = "test_create_registered_model";
        String modelDesc = "test_create_registered_model_desc";
        RegisteredModel response = client.createRegisteredModel(modelName, modelDesc);
        Assertions.assertEquals(modelDesc, response.getModelDesc());

        client.deleteRegisteredModel(modelName);
        Assertions.assertNull(client.getRegisteredModelDetail(modelName));
    }

    @Test
    public void testListRegisteredModel() throws Exception {
        String modelName = "test_list_registered_model";
        String modelDesc = "test_list_registered_model_desc";
        client.createRegisteredModel(modelName, modelDesc);
        client.createRegisteredModel(modelName + "_2", modelDesc + "_2");
        Assertions.assertEquals(2, client.listRegisteredModels().size());
        Assertions.assertEquals(modelName, client.listRegisteredModels().get(0).getModelName());
        Assertions.assertEquals(modelDesc, client.listRegisteredModels().get(0).getModelDesc());
    }

    @Test
    public void testGetRegisteredModelDetail() throws Exception {
        String modelName = "test_get_registered_model_detail";
        String modelDesc = "test get registered model detail";
        client.createRegisteredModel(modelName, modelDesc);

        String modelPath1 = "fs://source1.pkl";
        String modelType = "{\"flavor.version\":1}";
        String versionDesc = "test get registered model detail1";

        ModelVersion modelVersion = client.createModelVersion(modelName, modelPath1, modelType, versionDesc);
        Assertions.assertEquals("1", modelVersion.getModelVersion());

        RegisteredModel model = client.getRegisteredModelDetail(modelName);
        Assertions.assertEquals(modelDesc, model.getModelDesc());
        modelVersion = model.getLatestModelVersion();
        Assertions.assertEquals("1", modelVersion.getModelVersion());
        Assertions.assertEquals(modelPath1, modelVersion.getModelPath());
        Assertions.assertEquals(modelType, modelVersion.getModelType());
        Assertions.assertEquals(versionDesc, modelVersion.getVersionDesc());

        String modelPath2 = "fs://source1.pkl.2";
        ModelVersion modelVersion2 = client.createModelVersion(modelName, modelPath2, modelType, versionDesc);
        Assertions.assertEquals("2", modelVersion2.getModelVersion());
        RegisteredModel model2 = client.getRegisteredModelDetail(modelName);
        Assertions.assertEquals(modelDesc, model2.getModelDesc());
        modelVersion2 = model2.getLatestModelVersion();
        Assertions.assertEquals("2", modelVersion2.getModelVersion());
        Assertions.assertEquals(modelPath2, modelVersion2.getModelPath());
    }

    @Test
    public void testUpdateModelVersion() throws Exception {
        String modelName = "test_update_model_version";
        String modelDesc = "test update model version";
        client.createRegisteredModel(modelName, modelDesc);

        String modelPath1 = "fs://source1.pkl";
        String modelType = "{\"flavor.version\":1}";
        String versionDesc = "test update model version1";

        ModelVersion modelVersion = client.createModelVersion(modelName, modelPath1, modelType, versionDesc);
        Assertions.assertEquals("1", modelVersion.getModelVersion());

        String modelPath2 = "fs://source1.pkl.2";
        ModelVersion response = client.updateModelVersion(modelName, "1", modelPath2, modelType, modelDesc, ModelStage.VALIDATED);
        Assertions.assertEquals("1", response.getModelVersion());
        Assertions.assertEquals(modelPath2, response.getModelPath());
        Assertions.assertEquals(ModelStage.VALIDATED, response.getCurrentStage());
    }

    @Test
    public void testDeleteModelVersion() throws Exception {
        String modelName = "test_delete_model_version";
        String modelDesc = "test delete model version";
        client.createRegisteredModel(modelName, modelDesc);

        String modelPath = "fs://source1.pkl";
        String modelType = "{\"flavor.version\":1}";
        String versionDesc = "test delete model version1";

        ModelVersion modelVersion = client.createModelVersion(modelName, modelPath, modelType, versionDesc);
        Assertions.assertEquals("1", modelVersion.getModelVersion());

        ModelVersion detail = client.getModelVersionDetail(modelName, "1");
        Assertions.assertEquals(modelName, detail.getModelName());
        Assertions.assertEquals(modelPath, detail.getModelPath());
        Assertions.assertEquals("1", detail.getModelVersion());
        client.deleteModelVersion(modelName, "1");
        Assertions.assertNull(client.getModelVersionDetail(modelName, "1"));
    }

    // test notification service

    @Test
    public void testUpdateAndListNotification() throws Exception {
        String namespace = "namespace";
        String key = "send_event_key";
        String value1 = "send_event_value1";
        String eventType = "send_event_type";
        String context = "send_event_context";
        EventMeta event = client.sendEvent(namespace, key, value1, eventType, context);
        Assertions.assertEquals(value1, event.getValue());
        Assertions.assertTrue(event.getVersion() > 0);

        List<EventMeta> eventList = client.listEvents(namespace, Arrays.asList(key), 0, eventType, 0);
        Assertions.assertEquals(1, eventList.size());
        Assertions.assertEquals(key, eventList.get(0).getKey());
        Assertions.assertEquals(value1, eventList.get(0).getValue());
        Assertions.assertEquals(eventType, eventList.get(0).getEventType());

        String value2 = "send_event_value2";
        EventMeta event2 = client.sendEvent(namespace, key, value2, eventType, context);
        Assertions.assertEquals(event.getVersion() + 1, event2.getVersion());
        eventList = client.listEvents(namespace, Arrays.asList(key), 0, eventType, 0);
        Assertions.assertEquals(2, eventList.size());
        Assertions.assertEquals(key, eventList.get(1).getKey());
        Assertions.assertEquals(value2, eventList.get(1).getValue());
        Assertions.assertEquals(eventType, eventList.get(1).getEventType());
        eventList = client.listEvents(namespace, Arrays.asList(key), event.getVersion(), eventType, 0);
        Assertions.assertEquals(1, eventList.size());
        Assertions.assertEquals(key, eventList.get(0).getKey());
        Assertions.assertEquals(value2, eventList.get(0).getValue());
        Assertions.assertEquals(eventType, eventList.get(0).getEventType());
    }

    @Test
    public void testListenNotification() throws Exception {
        class TestWatcher implements EventWatcher {
            @Override
            public void process(List<EventMeta> list) {
                Assertions.assertTrue(list.size() > 0);
                for (EventMeta e: list) {
                    System.out.println(e);
                }
            }
        }
        TestWatcher watcher = new TestWatcher();

        String namespace = "namespace";
        String key = "send_event_key";
        String eventType = "send_event_type";
        String context = "send_event_context";
        client.startListenEvent(namespace, key, watcher, 0, eventType, 0);

        String value1 = "send_event_value1";
        String value2 = "send_event_value2";
        String value3 = "send_event_value3";
        client.sendEvent(namespace, key, value1, eventType, context);
        client.sendEvent(namespace, key, value2, eventType, context);
        Thread.sleep(10 * 1000);
        client.sendEvent(namespace, key, value3, eventType, context);
        Thread.sleep(1 * 1000);
        client.stopListenEvent(namespace, key);

        String key2 = "send_event_key_2";
        String eventType2 = "send_event_type_2";
        client.sendEvent(namespace, key2, value1, eventType2, context);
        client.sendEvent(namespace, key2, value2, eventType2, context);
        client.startListenEvent(namespace, key2, watcher, 0, eventType2, 0);
        Thread.sleep(10 * 1000);
        client.sendEvent(namespace, key2, value3, eventType2, context);
        Thread.sleep(1 * 1000);
        client.stopListenEvent(namespace, key2);
    }

    @Test
    public void testFalse() {
        Assertions.assertFalse(true);
    }
}