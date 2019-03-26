import go
from keras.layers import Activation, Dense, Input, Reshape
from keras.models import Model
from keras.optimizers import SGD
from keras.regularizers import l2

DECAY = 1e-5
L2_REGULARIZATION_FACTOR = 0.005
LEARNING_RATE = 0.05
MOMENTUM = 0.9


class Ai(object):
    def __init__(self, weight_file=None):
        if weight_file is None:
            area = go.SPAN * go.SPAN
            flattened_count = area * 8
            input_layer = Input(
                shape=(flattened_count,),
                batch_shape=(None, flattened_count),
                dtype='float32'
            )
            move_score = Activation('softmax')(
                Reshape((go.SPAN, go.SPAN, 3))(
                    Dense(
                        area * 3,
                        activation='elu',
                        kernel_regularizer=l2(L2_REGULARIZATION_FACTOR)
                    )(input_layer)
                )
            )
            move_score_confidence = Dense(
                1,
                activation='sigmoid',
                kernel_regularizer=l2(L2_REGULARIZATION_FACTOR)
            )(input_layer)
            pass_score = Activation('softmax')(
                Reshape((1, 1, 3))(
                    Dense(
                        3,
                        activation='elu',
                        kernel_regularizer=l2(L2_REGULARIZATION_FACTOR)
                    )(input_layer)
                )
            )
            pass_score_confidence = Dense(
                1,
                activation='sigmoid',
                kernel_regularizer=l2(L2_REGULARIZATION_FACTOR)
            )(input_layer)

            self.model = Model(
                inputs=input_layer,
                outputs=[move_score, move_score_confidence, pass_score, pass_score_confidence]
            )
            self.model.compile(
                optimizer=SGD(
                    lr=LEARNING_RATE,
                    momentum=MOMENTUM,
                    decay=DECAY
                )
            )
        else:
            pass
