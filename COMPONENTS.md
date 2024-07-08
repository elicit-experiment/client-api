# `NewComponent::FaceLandmark`



| Property                 | Result                                                                                                                                                     |
| ------------------------ |------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `NumberOfFaces`          | Number of faces to detect.                                                                                                                                 |
| `Landmarks`              | Return Landmark data                                                                                                                                       |
| `BlendShapes`            | Return Blendshapes data                                                                                                                                    |
| `FaceTransformation`     | Return the face transformation matrices                                                                                                                    |
| `StripZCoordinates`      | Strip Z coordinates from Landmarks data                                                                                                                    |
| `IncludeBlandshapes`     | `eyeLookInRight,eyeLookInLeft` Comma separates list of Blendshapes<br/>to include.<br/>Removes the faceLandmarks not belonging the the included BlendShape |
