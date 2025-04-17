# ----------- FILE: box_optimization.py -----------
import openmdao.api as om

# Volume component
class VolumeComp(om.ExplicitComponent):
    def setup(self):
        self.add_input('length', val=1.0)
        self.add_input('width', val=1.0)
        self.add_input('height', val=1.0)
        self.add_output('volume', val=1.0)

    def setup_partials(self):
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        outputs['volume'] = inputs['length'] * inputs['width'] * inputs['height']


# Surface area constraint component
class SurfaceAreaConstraint(om.ExplicitComponent):
    def setup(self):
        self.add_input('length', val=1.0)
        self.add_input('width', val=1.0)
        self.add_input('height', val=1.0)
        self.add_output('SA_constraint', val=0.0)

    def setup_partials(self):
        self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        L, W, H = inputs['length'], inputs['width'], inputs['height']
        surface_area = 2 * (L * W + W * H + H * L)
        outputs['SA_constraint'] = 10.0 - surface_area


# Build and solve the model
prob = om.Problem()
model = prob.model

model.add_subsystem('volume_comp', VolumeComp(), promotes=['*'])
model.add_subsystem('sa_constraint', SurfaceAreaConstraint(), promotes=['*'])

model.add_design_var('length', lower=0.1, upper=5.0)
model.add_design_var('width', lower=0.1, upper=5.0)
model.add_design_var('height', lower=0.1, upper=5.0)
model.add_objective('volume', scaler=-1)
model.add_constraint('SA_constraint', lower=0.0)

# Recorder setup
recorder = om.SqliteRecorder("cases_march5.sql")
prob.driver = om.ScipyOptimizeDriver()
prob.driver.add_recorder(recorder)
prob.driver.recording_options['record_objectives'] = True
prob.driver.recording_options['record_constraints'] = True
prob.driver.recording_options['record_desvars'] = True

prob.setup()
prob.set_val('length', 1.0)
prob.set_val('width', 1.0)
prob.set_val('height', 1.0)

prob.run_driver()
prob.cleanup()

print("Optimal volume:", prob.get_val("volume")[0])
print("Surface Area Constraint (should be ≥ 0):", prob.get_val("SA_constraint")[0])
