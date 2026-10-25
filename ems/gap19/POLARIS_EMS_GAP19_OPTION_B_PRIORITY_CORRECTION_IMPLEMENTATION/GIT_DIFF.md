# Git Diff Specification

Conceptual diff applied to `system/optimization/implementations/gap19_highs_native.py`:

```diff
@@ -314,16 +314,16 @@
-        # Add Objectives (Option B Priority Mapping 1, 2, 3, 4)
+        # Add Objectives (Option B Corrected Priority Mapping: J1 > J2 > J3 > J4)
         obj1 = highspy.HighsLinearObjective()
-        obj1.priority = 1; obj1.weight = 1.0; obj1.offset = 0.0; obj1.abs_tolerance = 0.0; obj1.rel_tolerance = 0.0
+        obj1.priority = 4; obj1.weight = 1.0; obj1.offset = 0.0; obj1.abs_tolerance = 0.0; obj1.rel_tolerance = 0.0
         obj1.coefficients = c1.tolist()

         obj2 = highspy.HighsLinearObjective()
-        obj2.priority = 2; obj2.weight = 1.0; obj2.offset = 0.0; obj2.abs_tolerance = 0.0; obj2.rel_tolerance = 0.0
+        obj2.priority = 3; obj2.weight = 1.0; obj2.offset = 0.0; obj2.abs_tolerance = 0.0; obj2.rel_tolerance = 0.0
         obj2.coefficients = c2.tolist()

         obj3 = highspy.HighsLinearObjective()
-        obj3.priority = 3; obj3.weight = 1.0; obj3.offset = 0.0; obj3.abs_tolerance = 0.0; obj3.rel_tolerance = 0.0
+        obj3.priority = 2; obj3.weight = 1.0; obj3.offset = 0.0; obj3.abs_tolerance = 0.0; obj3.rel_tolerance = 0.0
         obj3.coefficients = c3.tolist()

         obj4 = highspy.HighsLinearObjective()
-        obj4.priority = 4; obj4.weight = 1.0; obj4.offset = 0.0; obj4.abs_tolerance = 0.0; obj4.rel_tolerance = 0.0
+        obj4.priority = 1; obj4.weight = 1.0; obj4.offset = 0.0; obj4.abs_tolerance = 0.0; obj4.rel_tolerance = 0.0
         obj4.coefficients = c4.tolist()
```
